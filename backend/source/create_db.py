import psycopg2
from psycopg2 import sql
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

from config import Settings, settings


def database_exists(cursor, db_name: str) -> bool:
    cursor.execute(
        "SELECT 1 FROM pg_catalog.pg_database WHERE datname = %s", (db_name,)
    )
    return cursor.fetchone() is not None


def create_database(config: Settings | None = None) -> None:
    config = config or settings
    conn = psycopg2.connect(
        dbname="postgres",
        user=config.db_user,
        password=config.db_password,
        host=config.db_host,
        port=config.db_port,
        connect_timeout=5,
    )
    try:
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        with conn.cursor() as cur:
            if database_exists(cur, config.db_name):
                print(f"DB '{config.db_name}' already exists.")
            else:
                cur.execute(
                    sql.SQL("CREATE DATABASE {}").format(
                        sql.Identifier(config.db_name)
                    )
                )
                print(f"DB '{config.db_name}' created successfully.")
    finally:
        conn.close()


if __name__ == "__main__":
    create_database()
