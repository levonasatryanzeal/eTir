from peewee import CharField
from playhouse.migrate import migrate


def up(database, migrator):
    migrate(
        migrator.add_column(
            "user",
            "email",
            CharField(max_length=255, default="", unique=True),
        ),
        migrator.add_column(
            "user",
            "password_hash",
            CharField(max_length=255, default=""),
        ),
    )
