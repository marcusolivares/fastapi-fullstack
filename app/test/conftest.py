import pytest

from ..database import get_db
from ..main import app
from ..dependencies import get_current_user
from .utils import TestingSessionLocal


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
