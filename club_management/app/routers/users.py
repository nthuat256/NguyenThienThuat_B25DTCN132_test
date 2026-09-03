from fastapi import APIRouter, Depends
from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.core.exception import UserNotFoundException
from app.dependencies import get_current_user, require_admin
from app.db.database import get_db
from app.models.user import User
from app.schemas.user import UserResponse, UserUpdate

router = APIRouter(prefix='/users', tags=['users'])


@router.get("/me")
def get_me(
    current_user: User = Depends(get_current_user)
):
    return {
        "id": current_user.id,
        "email": current_user.email,
        "full_name": current_user.full_name,
        "role": current_user.role,
        "is_active": current_user.is_active,
        "created_at": current_user.created_at,
    }


@router.get('/', response_model=list[UserResponse], dependencies=[Depends(require_admin)])
def get_users(
    q: str | None = None,
    is_active: bool | None = None,
    db: Session = Depends(get_db),
):
    query = db.query(User)
    if q:
        like = f"%{q}%"
        query = query.filter(or_(User.email.ilike(like), User.full_name.ilike(like)))
    if is_active is not None:
        query = query.filter(User.is_active == is_active)
    return query.all()
