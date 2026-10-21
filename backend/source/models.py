from peewee import (
    AutoField,
    CharField,
    Check,
    ForeignKeyField,
    IntegerField,
    Model,
)

from source.database import db


class BaseModel(Model):
    class Meta:
        database = db


class ProjectStatus:
    DRAFT = "draft"
    ACTIVE = "active"
    ARCHIVED = "archived"

    CHOICES = (
        (DRAFT, "Draft"),
        (ACTIVE, "Active"),
        (ARCHIVED, "Archived"),
    )


class Project(BaseModel):
    project_id = AutoField(primary_key=True)
    project_name = CharField(max_length=255)
    project_status = CharField(
        max_length=20,
        default=ProjectStatus.DRAFT,
        choices=ProjectStatus.CHOICES,
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


class User(BaseModel):
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
    email = CharField(max_length=255, unique=True, index=True)
    password_hash = CharField(max_length=255)

    class Meta:
        table_name = "user"
