from peewee import (
    AutoField,
    CharField,
    ForeignKeyField,
    IntegerField,
    Model,
    PostgresqlDatabase,
)

import config
from source.database import db
from source.models import BaseModel, Project, ProjectStatus, User


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


def test_user_model_matches_required_schema():
    assert issubclass(User, BaseModel)
    assert User._meta.table_name == "user"
    assert set(User._meta.fields) == {
        "user_id",
        "project_id",
        "fname",
        "lname",
        "email",
        "password_hash",
    }

    user_id = User._meta.fields["user_id"]
    assert isinstance(user_id, AutoField)
    assert user_id.primary_key is True

    project_id = User._meta.fields["project_id"]
    assert isinstance(project_id, ForeignKeyField)
    assert project_id.rel_model is Project
    assert project_id.column_name == "project_id"
    assert project_id.on_delete == "CASCADE"
    assert hasattr(Project, "users")

    assert isinstance(User._meta.fields["fname"], CharField)
    assert User._meta.fields["fname"].max_length == 255
    assert isinstance(User._meta.fields["lname"], CharField)
    assert User._meta.fields["lname"].max_length == 255

    email = User._meta.fields["email"]
    assert isinstance(email, CharField)
    assert email.max_length == 255
    assert email.unique is True

    password_hash = User._meta.fields["password_hash"]
    assert isinstance(password_hash, CharField)
    assert password_hash.max_length == 255
