import aio_pika
import json
from app.core.config import settings


class RabbitMQService:
    def __init__(self):
        self.connection = None
        self.channel = None

    async def connect(self):
        self.connection = await aio_pika.connect_robust(
            host=settings.RABBITMQ_HOST,
            port=settings.RABBITMQ_PORT,
            login=settings.RABBITMQ_USER,
            password=settings.RABBITMQ_PASS
        )
        self.channel = await self.connection.channel()

    async def publish_message(self, message: dict, queue_name: str):
        if not self.channel:
            await self.connect()

        await self.channel.default_exchange.publish(
            aio_pika.Message(body=json.dumps(message).encode()),
            routing_key=queue_name
        )
        print(f"[x] Sent '{message}' to queue '{queue_name}'")

    async def close(self):
        if self.connection:
            await self.connection.close()


async def get_rabbitmq_service():
    service = RabbitMQService()
    await service.connect()
    try:
        yield service
    finally:
        await service.close()
rabbitmq_service = RabbitMQService()