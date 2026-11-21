# TodoApp: FastAPI + PostgreSQL

![Python](https://img.shields.io/badge/Python-3.10+-3776AB?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-009688?logo=fastapi&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-4169E1?logo=postgresql&logoColor=white)
![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-D71F00?logo=sqlalchemy&logoColor=white)
![pytest](https://img.shields.io/badge/tested%20with-pytest-0A9EDC?logo=pytest&logoColor=white)

A full-stack todo application that is **mostly backend**: a REST API built with **FastAPI** and
**PostgreSQL**, with JWT authentication, role-based access, and migrations. A **simple
server-rendered frontend** (Jinja2 + Bootstrap + vanilla JS) sits on top of the same API.

## Features

- **JWT auth**: register, log in with OAuth2 password flow, bcrypt-hashed passwords
- **Per-user todos**: full CRUD, each user only sees their own
- **Admin role**: router-level guard (`require_admin`) to list and delete any todo
- **Typed config**: settings loaded from `.env` with `pydantic-settings`, fails fast if missing
- **Response models**: Pydantic schemas control exactly what the API returns
- **Migrations** with Alembic
- **Tests** with pytest against a real PostgreSQL in Docker

## How it fits together

```mermaid
flowchart LR
    B[Browser] -->|HTML pages| P[Jinja2 templates]
    B -->|fetch + JWT| R[FastAPI routers<br/>auth · todos · users · admin]
    P --> R
    R --> D[Dependencies<br/>DB session · current user · admin]
    D --> S[(PostgreSQL<br/>via SQLAlchemy)]
```

## Tech stack

| Layer    | Tools                                                       |
|----------|-------------------------------------------------------------|
| API      | FastAPI, Pydantic, Uvicorn                                  |
| Data     | PostgreSQL, SQLAlchemy, Alembic, psycopg 3                  |
| Auth     | OAuth2 password flow, JWT (python-jose), bcrypt (passlib)   |
| Frontend | Jinja2 templates, Bootstrap, vanilla JS                     |
| Testing  | pytest, httpx `TestClient`, Docker Compose (test database)  |

## Project structure

```
TodoApp/
├── main.py            # app setup, static files, router registration
├── config.py          # typed settings loaded from .env
├── database.py        # engine, session, get_db
├── dependencies.py    # current user + admin guards
├── security.py        # password hashing, JWT creation
├── models.py          # SQLAlchemy models (Users, Todos)
├── schemas.py         # Pydantic request/response models
├── routers/           # pages (HTML) + auth, todos, users, admin (API)
├── templates/         # Jinja2 pages
├── static/            # CSS + JS
├── alembic/           # migrations
└── test/              # pytest suite
```

## Getting started

**Prerequisites:** Python 3.10+, a running PostgreSQL, and Docker (for the tests).

> The code is a Python package imported as `TodoApp` (relative imports, Alembic's `env.py`),
> so clone it into a folder with that name and run commands from its **parent** directory.

```bash
git clone https://github.com/marcusolivares/fastapi-fullstack.git TodoApp
python -m venv TodoApp/.venv
source TodoApp/.venv/bin/activate        # Windows: TodoApp\.venv\Scripts\activate
pip install -r TodoApp/requirements.txt
```

Create an empty PostgreSQL database, then copy `.env.example` to `TodoApp/.env` and fill it in:

```env
DATABASE_URL=postgresql://postgres:<password>@localhost/TodoApplicationDatabase
TEST_DATABASE_URL=postgresql://postgres:postgres@localhost:5433/todoapp_test
SECRET_KEY=<output of: python -c "import secrets; print(secrets.token_hex(32))">
```

Run the app (tables are created on startup):

```bash
uvicorn TodoApp.main:app --reload
```

- App: http://localhost:8000
- Interactive API docs: http://localhost:8000/docs

## API overview

| Method | Endpoint                          | Description               | Auth  |
|--------|-----------------------------------|---------------------------|-------|
| POST   | `/auth/`                          | Register a user           | -     |
| POST   | `/auth/token`                     | Log in, get a JWT         | -     |
| GET    | `/todos/`                         | List your todos           | User  |
| GET    | `/todos/todo/{id}`                | Get one todo              | User  |
| POST   | `/todos/todo`                     | Create a todo             | User  |
| PUT    | `/todos/todo/{id}`                | Update a todo             | User  |
| DELETE | `/todos/todo/{id}`                | Delete a todo             | User  |
| GET    | `/users/`                         | Current user's profile    | User  |
| PUT    | `/users/password`                 | Change password           | User  |
| PUT    | `/users/phone_number/{number}`    | Change phone number       | User  |
| GET    | `/admin/todo`                     | List all todos            | Admin |
| DELETE | `/admin/todo/{id}`                | Delete any todo           | Admin |
| GET    | `/healthy`                        | Health check              | -     |

## Running the tests

The suite runs against a disposable PostgreSQL container on port 5433:

```bash
docker compose -f TodoApp/docker-compose.yml up -d
pytest TodoApp/test
```

## Roadmap

The codebase is being refactored step by step. See [docs/refactor-plan.md](docs/refactor-plan.md)
for what's done and what's next.
