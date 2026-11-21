import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

from ..config import settings
from ..database import Base, get_db
from ..dependencies import get_current_user
from ..main import app
from ..models import Todos, Users
from ..security import bcrypt_context

assert settings.test_database_url, "TEST_DATABASE_URL must be set in .env to run the tests"

engine = create_engine(settings.test_database_url)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)


def override_get_db():
    with TestingSessionLocal() as db:
        yield db


def override_get_current_user():
    return {'username': 'codingwithrobytest', 'id': 1, 'user_role': 'admin'}


@pytest.fixture(autouse=True)
def override_dependencies():
    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_current_user] = override_get_current_user
    yield
    app.dependency_overrides.clear()


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def db():
    """A fresh session for checking what a request wrote. Query it after the request, not before:
    objects it already loaded wouldn't show the request's changes."""
    with TestingSessionLocal() as session:
        yield session


@pytest.fixture
def test_user():
    # Clean up at the start (not the end) so the last test's data stays for inspection
    with engine.connect() as connection:
        connection.execute(text("TRUNCATE users, todos RESTART IDENTITY CASCADE;"))
        connection.commit()

    user = Users(
        username="codingwithrobytest",
        email="codingwithrobytest@email.com",
        first_name="Eric",
        last_name="Roby",
        hashed_password=bcrypt_context.hash("testpassword"),
        role="admin",
        phone_number="(111)-111-1111"
    )

    with TestingSessionLocal() as session:
        session.add(user)
        session.commit()
        session.refresh(user)
    return user


@pytest.fixture
def test_todo(test_user):
    todo = Todos(
        title="Learn to code!",
        description="Need to learn everyday!",
        priority=5,
        complete=False,
        owner_id=1
    )

    with TestingSessionLocal() as session:
        session.add(todo)
        session.commit()
        session.refresh(todo)
    return todo
