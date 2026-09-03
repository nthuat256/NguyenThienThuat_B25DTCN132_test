from fastapi import Depends
from fastapi.security import APIKeyHeader
from sqlalchemy.orm import Session

from app.core.exception import (
    AccountLockedException,
    AdminRequiredException,
    InvalidTokenException,
)
from app.core.security import decode_access_token
from app.db.database import get_db
from app.models.user import User

token_scheme = APIKeyHeader(name="Authorization")

def get_current_user(
    token: str = Depends(token_scheme),
    db: Session = Depends(get_db),
) -> User:

    if token.startswith("Bearer "):
        token = token.split(" ")[1]

    payload = decode_access_token(token)
    if not payload or payload.get("type") != "access" or not payload.get("sub"):
        raise InvalidTokenException()

    try:
        user_id = int(payload["sub"])
    except (TypeError, ValueError):
        raise InvalidTokenException()

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise InvalidTokenException()
    if not user.is_active:
        raise AccountLockedException()
    return user


def require_admin(current_user: User = Depends(get_current_user)) -> User:
    if current_user.role != "ADMIN":
        raise AdminRequiredException()
    return current_user