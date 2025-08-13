import json
from app.core.config import settings
import aio_pika
from aio_pika import ExchangeType, IncomingMessage


class RabbitMQService:
    def __init__(self):
        self.connection = None
        self.channel = None
        self.queues = {}  # To store declared queues
        self.exchanges = {} # To store declared exchanges

    async def connect(self):
        if not self.connection or self.connection.is_closed:
            self.connection = await aio_pika.connect_robust(
                host=settings.RABBITMQ_HOST,
                port=settings.RABBITMQ_PORT,
                login=settings.RABBITMQ_USER,
                password=settings.RABBITMQ_PASS
            )
            self.channel = await self.connection.channel()
            # Ensure default exchange is available
            self.exchanges[''] = self.channel.default_exchange

    async def declare_exchange(self, name: str, type: ExchangeType = ExchangeType.DIRECT, **kwargs):
        if name not in self.exchanges:
            exchange = await self.channel.declare_exchange(name, type, **kwargs)
            self.exchanges[name] = exchange
        return self.exchanges[name]

    async def declare_queue(self, name: str, **kwargs):
        if name not in self.queues:
            queue = await self.channel.declare_queue(name, **kwargs)
            self.queues[name] = queue
        return self.queues[name]

    async def bind_queue(self, queue_name: str, exchange_name: str, routing_key: str = None):
        queue = self.queues.get(queue_name)
        exchange = self.exchanges.get(exchange_name)
        if queue and exchange:
            await queue.bind(exchange, routing_key or queue_name)
        else:
            raise ValueError(f"Queue '{queue_name}' or Exchange '{exchange_name}' not declared.")

    async def publish_message(self, message: dict, routing_key: str, exchange_name: str = '', exchange_type: ExchangeType = ExchangeType.DIRECT):
        if not self.channel:
            await self.connect()

        exchange = self.exchanges.get(exchange_name)
        if not exchange:
            # Declare exchange if it doesn't exist (or use default)
            # Ensure it's declared as durable=True to match existing queues/exchanges
            exchange = await self.declare_exchange(exchange_name, exchange_type, durable=True)

        await exchange.publish(
            aio_pika.Message(body=json.dumps(message).encode()),
            routing_key=routing_key
        )
        print(f"[x] Sent '{message}' to exchange '{exchange_name}' with routing key '{routing_key}'")

    async def start_consumer(self, queue_name: str, callback):
        if not self.channel:
            await self.connect()

        queue = self.queues.get(queue_name)
        if not queue:
            raise ValueError(f"Queue '{queue_name}' not declared.")

        print(f"[*] Waiting for messages in queue '{queue_name}'. To exit press CTRL+C")
        await queue.consume(callback)

    async def close(self):
        if self.connection and not self.connection.is_closed:
            await self.connection.close()


async def get_rabbitmq_service() -> RabbitMQService:
    """Dependency injection for RabbitMQService."""
    service = RabbitMQService()
    await service.connect()
    try:
        yield service
    finally:
        await service.close()
