from peewee import SchemaManager

from source.models import User


def up(database, migrator):
    SchemaManager(User, database=database).create_all(safe=True)
