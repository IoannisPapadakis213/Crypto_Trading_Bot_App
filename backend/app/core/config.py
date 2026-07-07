"""Runtime configuration, loaded from environment variables (`.env` in dev).

Nothing here is hardcoded — copy `.env.example` to `.env` and override as
needed. `get_settings()` is cached so the whole app shares one instance.
"""

from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

_DEFAULT_DB_PATH = Path(__file__).resolve().parents[2] / "data" / "app.db"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # CoinGecko free tier works without a key; set this only if you have a
    # Demo/Pro key and want the higher rate limit.
    coingecko_api_key: str | None = None
    coingecko_base_url: str = "https://api.coingecko.com/api/v3"

    database_url: str = f"sqlite+aiosqlite:///{_DEFAULT_DB_PATH.as_posix()}"

    market_universe_size: int = 100
    ranking_top_n: int = 10
    pipeline_interval_minutes: int = 15
    min_snapshots_for_volume_avg: int = 4

    candle_exchange_id: str = "kraken"
    candle_timeframe: str = "1h"

    # Comma-separated on purpose: pydantic-settings decodes list-typed env
    # fields as JSON, which is a surprising thing to require in a .env file.
    cors_origins: str = "http://localhost:3000,https://crypto-trading-bot-app.vercel.app"

    @property
    def cors_origins_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
