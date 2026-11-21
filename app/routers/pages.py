"""Server-rendered HTML pages. The JSON API lives in the other routers."""
from pathlib import Path

from fastapi import APIRouter, HTTPException, Request, status
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates

from ..dependencies import CookieUser, DbSession
from ..models import Todos

templates = Jinja2Templates(directory=Path(__file__).resolve().parent.parent / "templates")

# Pages aren't part of the API, so keep them out of /docs
router = APIRouter(include_in_schema=False)


@router.get("/")
def root():
    return RedirectResponse(url="/todos/todo-page", status_code=status.HTTP_302_FOUND)


@router.get("/auth/login-page")
def render_login_page(request: Request):
    return templates.TemplateResponse(request, "login.html")


@router.get("/auth/register-page")
def render_register_page(request: Request):
    return templates.TemplateResponse(request, "register.html")


@router.get("/todos/todo-page")
def render_todo_page(request: Request, user: CookieUser, db: DbSession):
    todos = db.query(Todos).filter(Todos.owner_id == user.get('id')).all()
    return templates.TemplateResponse(request, "todo.html", {"todos": todos, "user": user})


@router.get("/todos/add-todo-page")
def render_add_todo_page(request: Request, user: CookieUser):
    return templates.TemplateResponse(request, "add-todo.html", {"user": user})


@router.get("/todos/edit-todo-page/{todo_id}")
def render_edit_todo_page(request: Request, user: CookieUser, db: DbSession, todo_id: int):
    todo = db.query(Todos).filter(Todos.id == todo_id).filter(Todos.owner_id == user.get('id')).first()
    if todo is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Todo not found.')
    return templates.TemplateResponse(request, "edit-todo.html", {"todo": todo, "user": user})
