from pydantic import BaseModel, Field
from fastapi import APIRouter, HTTPException, Path
from ..models import Users
from ..dependencies import DbSession
from starlette import status
from .auth import CurrentUser
from passlib.context import CryptContext

router = APIRouter(
    prefix='/users',
    tags=['users']
)

bcrypt_context = CryptContext(schemes=['bcrypt'], deprecated='auto')


class UserVerification(BaseModel):
     password: str
     new_password: str = Field(min_length=6)

     

@router.get("/", status_code=status.HTTP_200_OK)
async def get_user(user: CurrentUser, db: DbSession):
    if user is None:
        raise HTTPException(status_code=401, detail='Authentication Failed')   
    return db.query(Users).filter(Users.id == user.get('id')).first()


@router.put("/password", status_code=status.HTTP_204_NO_CONTENT)
async def change_password(user: CurrentUser, db: DbSession, user_verification: UserVerification):
    if user is None:
        raise HTTPException(status_code=401, detail='Authentication Failed')

    user_model = db.query(Users).filter(Users.id == user.get('id')).first()

    if not bcrypt_context.verify(user_verification.password, user_model.hashed_password):
        raise HTTPException(status_code=401, detail='Error on password change')
    
    user_model.hashed_password = bcrypt_context.hash(user_verification.new_password)
    db.add(user_model)
    db.commit()


@router.put("/phone_number/{phone_number}", status_code=status.HTTP_204_NO_CONTENT)
async def change_phone_number(user: CurrentUser, db: DbSession, phone_number: str):
    if user is None:
        raise HTTPException(status_code=401, detail='Authentication Failed')

    user_model = db.query(Users).filter(Users.id == user.get('id')).first()

    user_model.phone_number = phone_number

    db.add(user_model)
    db.commit()