from urllib.parse import unquote, urlsplit

from peewee import PostgresqlDatabase

from config import settings


def database_from_url(url: str) -> PostgresqlDatabase:
    parsed = urlsplit(url)
    return PostgresqlDatabase(
        unquote(parsed.path.lstrip("/")),
        user=unquote(parsed.username or ""),
        password=unquote(parsed.password or ""),
        host=parsed.hostname or "localhost",
        port=parsed.port or 5432,
    )


db = database_from_url(settings.database_url)
