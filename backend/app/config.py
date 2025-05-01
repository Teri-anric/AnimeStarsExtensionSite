from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy.engine.url import URL
from pydantic import Field

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


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_nested_delimiter="__")

    database: DatabaseSettings
    parser: ParserSettings = Field(default_factory=ParserSettings)


settings = Settings()
