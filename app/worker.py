import asyncio
import logging
import json
import argparse
from aio_pika import IncomingMessage, ExchangeType
from app.services.rabbitmq import RabbitMQService
from app.tasks.message_tasks import process_initial_notification, process_retry_notification, process_final_notification, process_dlq_message
from app.core.config import settings

logger = logging.getLogger(__name__)

# Map queue names to their respective task functions
TASK_FUNCTIONS = {
    settings.NOTIFICATION_INPUT_QUEUE: process_initial_notification,
    settings.NOTIFICATION_RETRY_QUEUE: process_retry_notification,
    settings.NOTIFICATION_VALIDATION_QUEUE: process_final_notification,
    settings.NOTIFICATION_DLQ: process_dlq_message,
}

async def process_message(message: IncomingMessage, task_func, rabbitmq_service: RabbitMQService):
    async with message.process():
        try:
            data = json.loads(message.body.decode())
            await task_func(data, rabbitmq_service)
            logger.info(f"Message processed successfully by {task_func.__name__}")
        except Exception as e:
            logger.error(f"Error processing message for {task_func.__name__}: {e}", exc_info=True)
            # The retry/DLQ logic is now handled within the task functions themselves
            # No need for nack(requeue=False) here, as messages are explicitly routed.

async def main(queue_names_str: str):
    logging.basicConfig(level=logging.INFO)
    
    queue_names = [q.strip() for q in queue_names_str.split(',') if q.strip()]
    if not queue_names:
        logger.error("No queues specified to consume from.")
        return

    logger.info(f"Starting aio-pika worker(s) for queues: {', '.join(queue_names)}")

    rabbitmq_service = RabbitMQService()

    try:
        await rabbitmq_service.connect()
        logger.info("Connected to RabbitMQ.")

        consumer_tasks = []
        for queue_name in queue_names:
            if queue_name not in TASK_FUNCTIONS:
                logger.warning(f"Unknown queue name: {queue_name}. Skipping. Available queues: {', '.join(TASK_FUNCTIONS.keys())}")
                continue

            task_func = TASK_FUNCTIONS[queue_name]
            
            # Declare exchange and queue (ensure they are durable)
            exchange_name = f"{queue_name}_exchange"
            # For DLQ, we might need specific arguments for dead-lettering, but for now, simple declaration.
            await rabbitmq_service.declare_exchange(exchange_name, ExchangeType.DIRECT, durable=True)
            await rabbitmq_service.declare_queue(queue_name, durable=True)
            await rabbitmq_service.bind_queue(queue_name, exchange_name, routing_key=queue_name)
            logger.info(f"Exchange '{exchange_name}' and queue '{queue_name}' declared and bound.")

            # Start consuming messages for this queue in a separate task
            consumer_task = asyncio.create_task(
                rabbitmq_service.start_consumer(
                    queue_name,
                    lambda msg, tf=task_func: process_message(msg, tf, rabbitmq_service)
                )
            )
            consumer_tasks.append(consumer_task)
            logger.info(f"Consumer started for queue: {queue_name}")

        if not consumer_tasks:
            logger.warning("No valid queues found to start consumers for. Exiting worker.")
            return

        # Keep the event loop running indefinitely for background consumer tasks
        await asyncio.Future()

    except asyncio.CancelledError:
        logger.info("Worker stopped by cancellation.")
    except Exception as e:
        logger.error(f"Worker encountered an error: {e}", exc_info=True)
    finally:
        if rabbitmq_service:
            await rabbitmq_service.close()
            logger.info("RabbitMQ connection closed.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run aio-pika worker for specified queues.")
    parser.add_argument("--queue", required=True, help="Comma-separated list of queue names to consume messages from.")
    args = parser.parse_args()

    try:
        asyncio.run(main(args.queue))
    except KeyboardInterrupt:
        logger.info("Worker stopped manually.")
