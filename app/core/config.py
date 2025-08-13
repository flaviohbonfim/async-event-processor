from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    RABBITMQ_HOST: str = "rabbitmq"
    RABBITMQ_PORT: int = 5672
    RABBITMQ_USER: str = "guest"
    RABBITMQ_PASS: str = "guest"

    REDIS_HOST: str = "redis"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0

    NOTIFICATION_INPUT_QUEUE: str = "fila.notificacao.entrada"
    NOTIFICATION_RETRY_QUEUE: str = "fila.notificacao.retry"
    NOTIFICATION_VALIDATION_QUEUE: str = "fila.notificacao.validacao"
    NOTIFICATION_DLQ: str = "fila.notificacao.dlq"

    ALLOWED_NOTIFICATION_TYPES: list[str] = ["email", "sms", "push"]

    model_config = SettingsConfigDict(env_file=".env")


settings = Settings()
