from pydantic import BaseModel, Field
from fastapi import APIRouter, Depends, HTTPException, Path
from ..models import Todos
from ..dependencies import DbSession, require_admin
from starlette import status

router = APIRouter(
    prefix='/admin',
    tags=['admin'],
    dependencies=[Depends(require_admin)]
)


@router.get("/todo", status_code=status.HTTP_200_OK)
async def read_all(db: DbSession):
    return db.query(Todos).all()


@router.delete("/todo/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_todo(db: DbSession, todo_id: int = Path(gt=0)):
    todo_model = db.query(Todos).filter(Todos.id == todo_id).first()
    if todo_model is None:
        raise HTTPException(status_code=404, detail='Todo not found.')
    db.query(Todos).filter(Todos.id == todo_id).delete()
    db.commit()

