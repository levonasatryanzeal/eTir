import os
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import quote

from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_ENV_FILE = PROJECT_ROOT / ".env"


@dataclass(frozen=True)
class Settings:
    db_name: str
    db_user: str
    db_password: str
    db_host: str
    db_port: int

    @property
    def database_url(self) -> str:
        user = quote(self.db_user, safe="")
        password = quote(self.db_password, safe="")
        return (
            f"postgresql://{user}:{password}"
            f"@{self.db_host}:{self.db_port}/{self.db_name}"
        )


def _required(name: str) -> str:
    value = os.getenv(name, "").strip()
    if not value:
        raise RuntimeError(f"Missing required environment variable: {name}")
    return value


def _port() -> int:
    raw = _required("DB_PORT")
    try:
        return int(raw)
    except ValueError as exc:
        raise RuntimeError(f"Invalid DB_PORT value: {raw!r}") from exc


def load_settings(env_file: Path | None = None) -> Settings:
    load_dotenv(env_file or DEFAULT_ENV_FILE, override=False)
    return Settings(
        db_name=_required("DB_NAME"),
        db_user=_required("DB_USER"),
        db_password=_required("DB_PASSWORD"),
        db_host=_required("DB_HOST"),
        db_port=_port(),
    )


settings = load_settings()
