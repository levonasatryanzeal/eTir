from peewee import AutoField, CharField, Check, IntegerField, Model

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
