import re
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from peewee import IntegrityError
from pydantic import BaseModel, Field, field_validator

from source.models import Project, ProjectStatus, User
from source.security import hash_password

BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR / "static"
EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")

app = FastAPI()
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


class RegisterRequest(BaseModel):
    fname: str = Field(max_length=255)
    lname: str = Field(max_length=255)
    email: str = Field(max_length=255)
    password: str = Field(min_length=8, max_length=128)
    project_id: int = Field(gt=0)

    @field_validator("fname", "lname")
    @classmethod
    def validate_name(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("Имя не может быть пустым")
        return value

    @field_validator("email")
    @classmethod
    def validate_email(cls, value: str) -> str:
        value = value.strip().lower()
        if not EMAIL_RE.match(value):
            raise ValueError("Некорректный email")
        return value


@app.get("/")
def read_root():
    return {"message": "Hello eTir!"}


@app.get("/register", include_in_schema=False)
def register_page():
    return FileResponse(STATIC_DIR / "register.html")


@app.get("/api/projects")
def list_projects():
    projects = (
        Project.select()
        .where(Project.project_status != ProjectStatus.ARCHIVED)
        .order_by(Project.project_name)
    )
    return [
        {
            "project_id": project.project_id,
            "project_name": project.project_name,
        }
        for project in projects
    ]


@app.post("/api/register", status_code=201)
def register(payload: RegisterRequest):
    project = Project.get_or_none(
        (Project.project_id == payload.project_id)
        & (Project.project_status != ProjectStatus.ARCHIVED)
    )
    if project is None:
        raise HTTPException(status_code=400, detail="Проект не найден")

    if User.select().where(User.email == payload.email).exists():
        raise HTTPException(
            status_code=409, detail="Пользователь с таким email уже существует"
        )

    try:
        with User._meta.database.atomic():
            user = User.create(
                project_id=project,
                fname=payload.fname,
                lname=payload.lname,
                email=payload.email,
                password_hash=hash_password(payload.password),
            )
    except IntegrityError as exc:
        raise HTTPException(
            status_code=409, detail="Пользователь с таким email уже существует"
        ) from exc

    return {
        "user_id": user.user_id,
        "fname": user.fname,
        "lname": user.lname,
        "email": user.email,
        "project_id": project.project_id,
    }
