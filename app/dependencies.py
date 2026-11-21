from typing import Annotated

from fastapi import Cookie, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from .config import settings
from .database import get_db

oauth2_bearer = OAuth2PasswordBearer(tokenUrl='auth/token')

DbSession = Annotated[Session, Depends(get_db)]


class NotAuthenticated(Exception):
    """A page was requested without a valid session cookie. main.py redirects it to the login page."""


def decode_token(token: str | None) -> dict | None:
    """Return the user in a JWT, or None if the token is missing, invalid or expired."""
    if not token:
        return None
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
    except JWTError:
        return None
    username: str = payload.get('sub')
    user_id: int = payload.get('id')
    if username is None or user_id is None:
        return None
    return {'username': username, 'id': user_id, 'user_role': payload.get('role')}


async def get_current_user(token: Annotated[str, Depends(oauth2_bearer)]):
    user = decode_token(token)
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Could not validate user.')
    return user


CurrentUser = Annotated[dict, Depends(get_current_user)]


async def get_current_user_from_cookie(access_token: Annotated[str | None, Cookie()] = None) -> dict:
    """Pages authenticate with the cookie that base.js sets at login, not an Authorization header."""
    user = decode_token(access_token)
    if user is None:
        raise NotAuthenticated
    return user


CookieUser = Annotated[dict, Depends(get_current_user_from_cookie)]


async def require_admin(user: CurrentUser) -> dict:
    if user.get('user_role') != 'admin':
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Admin privileges required.')
    return user
