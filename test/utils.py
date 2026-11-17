from sqlalchemy import create_engine, text
from fastapi.testclient import TestClient
from sqlalchemy.orm import sessionmaker
from ..config import settings
from ..database import Base
from ..main import app
import pytest
from ..models import Todos, Users
from ..security import bcrypt_context

assert settings.test_database_url, "TEST_DATABASE_URL must be set in TodoApp/.env to run the tests"

engine = create_engine(settings.test_database_url)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)

client = TestClient(app)

@pytest.fixture
def test_todo(test_user):
    todo = Todos(
        title="Learn to code!",
        description="Need to learn everyday!",
        priority=5,
        complete=False,
        owner_id=1
    )

    with TestingSessionLocal() as db:
        db.add(todo)
        db.commit()
        db.refresh(todo)
    return todo


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

    with TestingSessionLocal() as db:
        db.add(user)
        db.commit()
        db.refresh(user)
    return user
