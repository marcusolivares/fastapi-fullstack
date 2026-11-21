from fastapi import status
from ..dependencies import get_current_user
from ..main import app
from ..models import Todos


def test_admin_read_all_authenticated(client, test_todo):
    response = client.get("/admin/todo")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == [{'complete': False, 'title': 'Learn to code!', 'description': 'Need to learn everyday!',
                                'id': 1, 'priority': 5, 'owner_id': 1}]


def test_admin_delete_todo(client, db, test_todo):
    response = client.delete("/admin/todo/1")
    assert response.status_code == 204
    model = db.query(Todos).filter(Todos.id == 1).first()
    assert model is None


def test_admin_delete_todo_not_found(client, test_todo):
    response = client.delete("/admin/todo/9999")
    assert response.status_code == 404
    assert response.json() == {'detail': 'Todo not found.'}


def test_admin_forbidden_for_non_admin(client):
    app.dependency_overrides[get_current_user] = lambda: {'username': 'regular', 'id': 2, 'user_role': 'user'}
    response = client.get("/admin/todo")
    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert response.json() == {'detail': 'Admin privileges required.'}
