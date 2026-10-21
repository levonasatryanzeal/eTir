from peewee import (
    AutoField,
    CharField,
    ForeignKeyField,
    Model,
    SchemaManager,
)


def up(database, migrator):
    class Project(Model):
        project_id = AutoField(primary_key=True)

        class Meta:
            table_name = "project"

    class User(Model):
        user_id = AutoField(primary_key=True)
        project_id = ForeignKeyField(
            Project,
            field=Project.project_id,
            column_name="project_id",
            backref="users",
            on_delete="CASCADE",
        )
        fname = CharField(max_length=255)
        lname = CharField(max_length=255)

        class Meta:
            table_name = "user"

    Project.bind(database, bind_refs=False, bind_backrefs=False)
    User.bind(database, bind_refs=False, bind_backrefs=False)
    SchemaManager(User, database=database).create_all(safe=True)
