from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    RABBITMQ_HOST: str = "rabbitmq"
    RABBITMQ_PORT: int = 5672
    RABBITMQ_USER: str = "guest"
    RABBITMQ_PASS: str = "guest"

    REDIS_HOST: str = "redis" # Default for Docker Compose
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0 # Default Redis DB

    model_config = SettingsConfigDict(env_file=".env")


settings = Settings()
