from fastapi import APIRouter, HTTPException, Path
from ..models import Users
from ..dependencies import CurrentUser, DbSession
from ..schemas import UserResponse, UserVerification
from ..security import bcrypt_context
from starlette import status

router = APIRouter(
    prefix='/users',
    tags=['users']
)


@router.get("/", status_code=status.HTTP_200_OK, response_model=UserResponse)
def get_user(user: CurrentUser, db: DbSession):
    return db.query(Users).filter(Users.id == user.get('id')).first()


@router.put("/password", status_code=status.HTTP_204_NO_CONTENT)
def change_password(user: CurrentUser, db: DbSession, user_verification: UserVerification):
    user_model = db.query(Users).filter(Users.id == user.get('id')).first()

    if not bcrypt_context.verify(user_verification.password, user_model.hashed_password):
        raise HTTPException(status_code=401, detail='Error on password change')
    
    user_model.hashed_password = bcrypt_context.hash(user_verification.new_password)
    db.add(user_model)
    db.commit()


@router.put("/phone_number/{phone_number}", status_code=status.HTTP_204_NO_CONTENT)
def change_phone_number(user: CurrentUser, db: DbSession, phone_number: str):
    user_model = db.query(Users).filter(Users.id == user.get('id')).first()

    user_model.phone_number = phone_number

    db.add(user_model)
    db.commit()