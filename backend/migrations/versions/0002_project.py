from peewee import (
    AutoField,
    CharField,
    Check,
    IntegerField,
    Model,
    SchemaManager,
)


def up(database, migrator):
    class Project(Model):
        project_id = AutoField(primary_key=True)
        project_name = CharField(max_length=255)
        project_status = CharField(
            max_length=20,
            default="draft",
            constraints=[
                Check("project_status IN ('draft', 'active', 'archived')")
            ],
        )
        users_count = IntegerField(
            default=0,
            constraints=[Check("users_count >= 0")],
        )

        class Meta:
            table_name = "project"

    Project.bind(database, bind_refs=False, bind_backrefs=False)
    SchemaManager(Project, database=database).create_all(safe=True)
