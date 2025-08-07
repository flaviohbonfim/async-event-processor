from fastapi import FastAPI
from app.api.endpoints import messages
from app.core.config import settings

app = FastAPI(
    title="RabbitMQ FastAPI Project",
    description="API for managing RabbitMQ messages with FastAPI and Celery",
    version="0.0.1",
)


@app.get("/health", tags=["Health Check"])
async def health_check():
    return {"status": "ok"}


app.include_router(messages.router, prefix="/api", tags=["Messages"])