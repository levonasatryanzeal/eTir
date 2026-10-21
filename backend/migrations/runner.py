import datetime
import importlib.util
from dataclasses import dataclass
from pathlib import Path
from typing import Callable

from peewee import (
    CharField,
    Database,
    DateTimeField,
    Model,
    MySQLDatabase,
    PostgresqlDatabase,
    SqliteDatabase,
)
from playhouse.migrate import (
    MySQLMigrator,
    PostgresqlMigrator,
    SchemaMigrator,
    SqliteMigrator,
)

VERSIONS_DIR = Path(__file__).resolve().parent / "versions"


@dataclass(frozen=True)
class Migration:
    name: str
    up: Callable[[Database, SchemaMigrator], None]


def _history_model(db: Database) -> type[Model]:
    class MigrationHistory(Model):
        name = CharField(primary_key=True)
        applied_at = DateTimeField(default=datetime.datetime.now)

        class Meta:
            database = db
            table_name = "etir_migrations"

    return MigrationHistory


def _migrator_for(db: Database) -> SchemaMigrator:
    if isinstance(db, PostgresqlDatabase):
        return PostgresqlMigrator(db)
    if isinstance(db, SqliteDatabase):
        return SqliteMigrator(db)
    if isinstance(db, MySQLDatabase):
        return MySQLMigrator(db)
    raise TypeError(f"Unsupported database type: {type(db).__name__}")


def discover_migrations(directory: Path | None = None) -> list[Migration]:
    base = directory or VERSIONS_DIR
    migrations = []
    for path in sorted(base.glob("[0-9]*.py")):
        spec = importlib.util.spec_from_file_location(
            f"migrations.versions.{path.stem}", path
        )
        if spec is None or spec.loader is None:
            raise ImportError(f"Cannot load migration: {path}")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        migrations.append(Migration(name=path.stem, up=module.up))
    return migrations


def apply_migrations(
    db: Database, migrations: list[Migration] | None = None
) -> list[str]:
    pending_source = migrations if migrations is not None else discover_migrations()
    history = _history_model(db)
    db.create_tables([history], safe=True)
    applied = {row.name for row in history.select(history.name)}

    applied_now = []
    for migration in pending_source:
        if migration.name in applied:
            continue
        migrator = _migrator_for(db)
        with db.atomic():
            migration.up(db, migrator)
            history.create(name=migration.name)
        applied_now.append(migration.name)
    return applied_now


if __name__ == "__main__":
    from source.database import db

    for name in apply_migrations(db):
        print(f"Applied migration: {name}")
