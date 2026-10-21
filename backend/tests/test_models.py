from peewee import AutoField, IntegerField, Model, PostgresqlDatabase

import config
from source.database import db
from source.models import BaseModel, Project, ProjectStatus


def test_base_model_is_peewee_model_bound_to_shared_database():
    assert issubclass(BaseModel, Model)
    assert BaseModel._meta.database is db
    assert isinstance(db, PostgresqlDatabase)


def test_database_uses_credentials_from_single_dsn():
    assert db.database == config.settings.db_name
    assert db.connect_params["user"] == config.settings.db_user
    assert db.connect_params["password"] == config.settings.db_password
    assert db.connect_params["host"] == config.settings.db_host
    assert db.connect_params["port"] == config.settings.db_port


def test_project_model_matches_required_schema():
    assert issubclass(Project, BaseModel)
    assert Project._meta.table_name == "project"
    assert set(Project._meta.fields) == {
        "project_id",
        "project_name",
        "project_status",
        "users_count",
    }

    project_id = Project._meta.fields["project_id"]
    assert isinstance(project_id, AutoField)
    assert project_id.primary_key is True

    assert Project._meta.fields["project_name"].max_length == 255
    project_status = Project._meta.fields["project_status"]
    assert project_status.default == ProjectStatus.DRAFT
    assert project_status.choices == ProjectStatus.CHOICES

    users_count = Project._meta.fields["users_count"]
    assert isinstance(users_count, IntegerField)
    assert users_count.default == 0


def test_project_status_has_expected_choices():
    assert ProjectStatus.DRAFT == "draft"
    assert ProjectStatus.ACTIVE == "active"
    assert ProjectStatus.ARCHIVED == "archived"
    assert ProjectStatus.CHOICES == (
        (ProjectStatus.DRAFT, "Draft"),
        (ProjectStatus.ACTIVE, "Active"),
        (ProjectStatus.ARCHIVED, "Archived"),
    )
