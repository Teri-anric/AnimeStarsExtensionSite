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
    cookie_file: str = "cookie.json"
    login: str = "teri-test"
    password: str = "testtest"
    code_expire_hours: int = 1


class AuthSettings(BaseSettings):
    secret_key: str = token_hex(32)
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60 * 24 * 7  # 7 days


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_nested_delimiter="__")

    database: DatabaseSettings
    parser: ParserSettings = Field(default_factory=ParserSettings)
    pm: PMSettings = Field(default_factory=PMSettings)
    auth: AuthSettings = Field(default_factory=AuthSettings)


settings = Settings()
