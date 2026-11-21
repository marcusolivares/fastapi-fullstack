from datetime import datetime, timedelta, timezone

from jose import jwt
from passlib.context import CryptContext

from .config import settings

bcrypt_context = CryptContext(schemes=['bcrypt'], deprecated='auto')


def create_access_token(username: str, user_id: int, role: str, expires_delta: timedelta):
    encode = {'sub': username, 'id': user_id, 'role': role}
    expires = datetime.now(timezone.utc) + expires_delta
    encode.update({'exp': expires})
    return jwt.encode(encode, settings.secret_key, algorithm=settings.algorithm)
