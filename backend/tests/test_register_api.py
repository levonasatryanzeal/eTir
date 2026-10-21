import pytest
from fastapi.testclient import TestClient
from peewee import SqliteDatabase

from main import app
from source.database import db
from source.models import Project, ProjectStatus, User
from source.security import verify_password


@pytest.fixture
def client(tmp_path):
    test_db = SqliteDatabase(str(tmp_path / "api.db"))
    User.bind(test_db)
    Project.bind(test_db)
    test_db.create_tables([Project, User])
    Project.create(
        project_name="qa1",
        project_status=ProjectStatus.ACTIVE,
    )

    with TestClient(app) as test_client:
        yield test_client, test_db

    test_db.close()
    User.bind(db)
    Project.bind(db)


def valid_payload(**overrides):
    payload = {
        "fname": "Levon",
        "lname": "Asatryan",
        "email": "levon@example.com",
        "password": "secret123",
        "project_id": 1,
    }
    payload.update(overrides)
    return payload


def test_register_page_returns_html(client):
    test_client, _ = client

    response = test_client.get("/register")

    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]
    assert "Регистрация" in response.text


def test_projects_endpoint_returns_non_archived_projects(client):
    test_client, test_db = client
    Project.create(project_name="old", project_status=ProjectStatus.ARCHIVED)

    response = test_client.get("/api/projects")

    assert response.status_code == 200
    assert response.json() == [{"project_id": 1, "project_name": "qa1"}]


def test_register_creates_user_with_hashed_password(client):
    test_client, _ = client

    response = test_client.post("/api/register", json=valid_payload())

    assert response.status_code == 201
    body = response.json()
    assert body["email"] == "levon@example.com"
    assert body["project_id"] == 1
    assert "password" not in body
    user = User.get(User.email == "levon@example.com")
    assert user.fname == "Levon"
    assert user.lname == "Asatryan"
    assert user.password_hash != "secret123"
    assert verify_password("secret123", user.password_hash) is True


def test_register_normalizes_email_to_lowercase(client):
    test_client, _ = client

    response = test_client.post(
        "/api/register", json=valid_payload(email="Levon@Example.COM")
    )

    assert response.status_code == 201
    assert response.json()["email"] == "levon@example.com"


def test_register_rejects_duplicate_email(client):
    test_client, _ = client
    test_client.post("/api/register", json=valid_payload())

    response = test_client.post(
        "/api/register", json=valid_payload(email="LEVON@example.com")
    )

    assert response.status_code == 409


def test_register_rejects_short_password(client):
    test_client, _ = client

    response = test_client.post(
        "/api/register", json=valid_payload(password="short")
    )

    assert response.status_code == 422


def test_register_rejects_unknown_project(client):
    test_client, _ = client

    response = test_client.post(
        "/api/register", json=valid_payload(project_id=999)
    )

    assert response.status_code == 400


def test_register_rejects_blank_name(client):
    test_client, _ = client

    response = test_client.post(
        "/api/register", json=valid_payload(fname="   ")
    )

    assert response.status_code == 422


def test_register_rejects_invalid_email(client):
    test_client, _ = client

    response = test_client.post(
        "/api/register", json=valid_payload(email="not-an-email")
    )

    assert response.status_code == 422
