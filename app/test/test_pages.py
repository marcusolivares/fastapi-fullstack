from datetime import timedelta

import pytest
from fastapi import status
from fastapi.testclient import TestClient

from ..database import get_db
from ..main import app
from ..security import create_access_token


def login_cookie(user_id: int) -> dict:
    """Pages authenticate like the browser does: with the access_token cookie, not a bearer header."""
    token = create_access_token('codingwithrobytest', user_id, 'admin', timedelta(minutes=5))
    return {'access_token': token}


@pytest.mark.parametrize('cookies', [{}, {'access_token': 'not-a-jwt'}], ids=['no cookie', 'invalid cookie'])
def test_page_redirects_to_login_without_valid_cookie(cookies):
    response = TestClient(app, cookies=cookies).get('/todos/todo-page', follow_redirects=False)

    assert response.status_code == status.HTTP_302_FOUND
    assert response.headers['location'] == '/auth/login-page'
    assert response.headers['set-cookie'].startswith('access_token=')
    assert 'Max-Age=0' in response.headers['set-cookie']


def test_page_error_is_not_turned_into_login_redirect():
    class BrokenSession:
        def query(self, *args):
            raise RuntimeError('database is down')

    def broken_db():
        yield BrokenSession()

    app.dependency_overrides[get_db] = broken_db
    client = TestClient(app, cookies=login_cookie(1), raise_server_exceptions=False)

    response = client.get('/todos/todo-page', follow_redirects=False)
    assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR


def test_todo_page_lists_own_todos(test_todo):
    response = TestClient(app, cookies=login_cookie(1)).get('/todos/todo-page')

    assert response.status_code == status.HTTP_200_OK
    assert 'Learn to code!' in response.text


def test_edit_todo_page_renders_own_todo(test_todo):
    response = TestClient(app, cookies=login_cookie(1)).get('/todos/edit-todo-page/1')

    assert response.status_code == status.HTTP_200_OK
    assert 'value="Learn to code!"' in response.text


def test_edit_todo_page_hides_other_users_todo(test_todo):
    response = TestClient(app, cookies=login_cookie(2)).get('/todos/edit-todo-page/1')

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert 'Learn to code!' not in response.text


@pytest.mark.parametrize('path', ['/auth/login-page', '/auth/register-page'])
def test_page_content_renders_inside_layout(path):
    html = TestClient(app).get(path).text

    assert html.index('<form') < html.index('</body>')
    assert html.rstrip().endswith('</html>')


def test_pages_are_not_in_api_docs():
    paths = TestClient(app).get('/openapi.json').json()['paths']

    assert not [p for p in paths if '-page' in p]
