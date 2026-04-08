from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy.engine.url import URL
from pydantic import Field
from secrets import token_hex


class DatabaseSettings(BaseSettings):
    user: str
    password: str
    host: str
    port: int
    db: str

    @property
    def url(self) -> URL:
        return URL.create(
            "postgresql+asyncpg",
            username=self.user,
            password=self.password,
            host=self.host,
            port=self.port,
            database=self.db,
        )

    @property
    def sync_url(self) -> URL:
        return URL.create(
            "postgresql",
            username=self.user,
            password=self.password,
            host=self.host,
            port=self.port,
            database=self.db,
        )


class ParserSettings(BaseSettings):
    proxy: str | None = None
    base_url: str | None = None


class PMSettings(BaseSettings):
    cookie_file: str | None = None
    login: str | None = None
    password: str | None = None


class AuthSettings(BaseSettings):
    secret_key: str = token_hex(32)
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60 * 24 * 7  # 7 days
    code_expire_minutes: int = 60  # 1 hour


class RedisSettings(BaseSettings):
    host: str = "localhost"
    port: int = 6379
    db: int = 0
    password: str | None = None
    username: str | None = None
    ssl: bool = False
    socket_timeout_seconds: float = 2.0


class CardBulkSettings(BaseSettings):
    flush_interval_seconds: int = 5
    flush_batch_size: int = 500
    key_prefix: str = "card_bulk"
    lock_ttl_seconds: int = 30


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_nested_delimiter="__")

    database: DatabaseSettings
    parser: ParserSettings = Field(default_factory=ParserSettings)
    pm: PMSettings = Field(default_factory=PMSettings)
    auth: AuthSettings = Field(default_factory=AuthSettings)
    # LOG_JSON — one JSON object per line (uvicorn, app loggers, http audit). See .env.exemple.
    log_json: bool = True
    # LOG_HTTP_BODIES / LOG_HTTP_BODY_MAX_BYTES — see .env.exemple (security-sensitive)
    log_http_bodies: bool = False
    log_http_body_max_bytes: int = Field(default=4096, ge=256, le=1_048_576)
    # SQLAlchemy / Postgres metrics → Prometheus (/metrics) for Grafana
    db_metrics_refresh_seconds: float = Field(default=15.0, ge=5.0, le=600.0)
    db_metrics_pg_stats: bool = True
    redis: RedisSettings = Field(default_factory=RedisSettings)
    card_bulk: CardBulkSettings = Field(default_factory=CardBulkSettings)


settings = Settings()
