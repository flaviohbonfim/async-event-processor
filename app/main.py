from fastapi import FastAPI
from app.api.endpoints import messages
from app.core.config import settings
from app.services.rabbitmq import RabbitMQService
from aio_pika import ExchangeType
app = FastAPI(
    title="RabbitMQ FastAPI Project",
    description="API for managing RabbitMQ messages with FastAPI and aio-pika",
    version="0.0.1",
)

rabbitmq_service: RabbitMQService = None

ALL_QUEUES = [
    settings.NOTIFICATION_INPUT_QUEUE,
    settings.NOTIFICATION_RETRY_QUEUE,
    settings.NOTIFICATION_VALIDATION_QUEUE,
    settings.NOTIFICATION_DLQ,
]

@app.on_event("startup")
async def startup_event():
    global rabbitmq_service
    rabbitmq_service = RabbitMQService()
    await rabbitmq_service.connect()

    for queue_name in ALL_QUEUES:
        exchange_name = f"{queue_name}_exchange"
        await rabbitmq_service.declare_exchange(exchange_name, ExchangeType.DIRECT, durable=True)
        await rabbitmq_service.declare_queue(queue_name, durable=True)
        await rabbitmq_service.bind_queue(queue_name, exchange_name, routing_key=queue_name)
    print("RabbitMQ topology declared by FastAPI app.")

@app.on_event("shutdown")
async def shutdown_event():
    if rabbitmq_service:
        await rabbitmq_service.close()
        print("RabbitMQ connection closed.")

@app.get("/health", tags=["Health Check"])
async def health_check():
    return {"status": "ok"}

app.include_router(messages.router, prefix="/api", tags=["Messages"])
