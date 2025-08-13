from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    RABBITMQ_HOST: str = "rabbitmq"
    RABBITMQ_PORT: int = 5672
    RABBITMQ_USER: str = "guest"
    RABBITMQ_PASS: str = "guest"

    REDIS_HOST: str = "redis"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0

    NOTIFICATION_INPUT_QUEUE: str = "fila.notificacao.entrada.SEU-NOME"
    NOTIFICATION_RETRY_QUEUE: str = "fila.notificacao.retry.SEU-NOME"
    NOTIFICATION_VALIDATION_QUEUE: str = "fila.notificacao.validacao.SEU-NOME"
    NOTIFICATION_DLQ: str = "fila.notificacao.dlq.SEU-NOME"
    NOTIFICATION_STATUS_UPDATE_QUEUE: str = "fila.notificacao.status.SEU-NOME"

    ALLOWED_NOTIFICATION_TYPES: list[str] = ["email", "sms", "push"]

    model_config = SettingsConfigDict(env_file=".env")


settings = Settings()
