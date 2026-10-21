from peewee import SchemaManager

from source.models import Project


def up(database, migrator):
    SchemaManager(Project, database=database).create_all(safe=True)
