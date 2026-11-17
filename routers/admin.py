from pydantic import BaseModel, Field
from fastapi import APIRouter, HTTPException, Path
from ..models import Todos
from ..dependencies import DbSession
from starlette import status
from .auth import CurrentUser

router = APIRouter(
    prefix='/admin',
    tags=['admin']
)


@router.get("/todo", status_code=status.HTTP_200_OK)
async def read_all(user: CurrentUser, db: DbSession):
    if user is None or user.get('user_role') != 'admin':
        raise HTTPException(status_code=401, detail='Authentication Failed')
    return db.query(Todos).all()


@router.delete("/todo/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_todo(user: CurrentUser, db: DbSession, todo_id: int = Path(gt=0)):
    if user is None or user.get('user_role') != 'admin':
        raise HTTPException(status_code=401, detail='Authentication Failed')
    todo_model = db.query(Todos).filter(Todos.id == todo_id).first()
    if todo_model is None:
        raise HTTPException(status_code=404, detail='Todo not found.')
    db.query(Todos).filter(Todos.id == todo_id).delete()
    db.commit()

