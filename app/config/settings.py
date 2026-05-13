from pydantic import Field, PostgresDsn
from pydantic_settings import BaseSettings, SettingsConfigDict


class BaseConfig(BaseSettings):
    """Базовый класс для конфигурации приложения"""

    environment: str = Field(alias="ENV", default="tests")

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_ignore_empty=True,
        extra="ignore",
    )


class ApplicationConfig(BaseConfig):
    """Конфигурация для приложения"""

    service_name: str = Field(alias="APP_SERVICE_NAME", default="app")
    port: int = Field(alias="APP_PORT", default=8000)
    host: str = Field(alias="APP_HOST", default="0.0.0.0")
    path_prefix: str = Field(alias="PATH_PREFIX", default="/api")


class DatabaseConfig(BaseConfig):
    user: str = Field(alias="DATABASE_USERNAME", default="test_user")
    name: str = Field(alias="DATABASE_NAME", default="test_db")
    password: str = Field(alias="DATABASE_PASSWORD", default="test_password")
    port: int = Field(alias="DATABASE_PORT", default=5432)
    host: str = Field(alias="DATABASE_HOST", default="localhost")
    ssl_cert_path: str = Field(alias="DATABASE_SSL_CERT", default="")

    @property
    def dsn(self) -> str:
        return str(
            PostgresDsn.build(
                scheme="postgresql+asyncpg",
                username=self.user,
                password=self.password,
                host=self.host,
                port=self.port,
                path=f"{self.name}",
            )
        )


class RedisConfig(BaseConfig):
    host: str = Field(alias="REDIS_HOST", default="localhost")
    port: int = Field(alias="REDIS_PORT", default=6379)
    db: int = Field(alias="REDIS_DB", default=0)
    password: str = Field(alias="REDIS_PASSWORD", default="")

    @property
    def dsn(self) -> str:
        auth_part = f":{self.password}@" if self.password else ""
        return f"redis://{auth_part}{self.host}:{self.port}/{self.db}"


class CacheConfig(BaseConfig):
    prefix: str = Field(alias="CACHE_PREFIX", default="fastapi-cache")
    default_ttl_seconds: int = Field(alias="CACHE_EXPIRE_SECONDS", default=172800)
    reset_hour: int = Field(alias="CACHE_RESET_HOUR", default=14)
    reset_minute: int = Field(alias="CACHE_RESET_MINUTE", default=11)


class Config:
    app = ApplicationConfig()
    database = DatabaseConfig()
    redis = RedisConfig()
    cache = CacheConfig()


settings = Config()
