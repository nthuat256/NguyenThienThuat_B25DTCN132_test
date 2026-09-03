from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.core.exception import AdminRequiredException
from app.core.exception import (
    AccountLockedException,
    EmailAlreadyRegisteredException,
    InvalidCredentialsException,
    InvalidRefreshTokenException,
)
from app.dependencies import get_current_user
from app.core.rate_limit import rate_limit_login
from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_access_token,
    hash_password,
    verify_password,
)
from app.db.database import get_db
from app.models.user import User
from app.schemas.user import (
    AccessTokenResponse,
    LoginRequest,
    RefreshRequest,
    TokenResponse,
    UserCreate,
    UserResponse,
)

router = APIRouter(prefix='/auth', tags=['auth'])

@router.post(
    "/register",
    status_code=status.HTTP_201_CREATED
)
def register(
    user_data: UserCreate,
    db: Session = Depends(get_db)
):
    if db.query(User).filter(
        User.email == user_data.email
    ).first():
        raise EmailAlreadyRegisteredException()

    user = User(
        email=user_data.email,
        password_hash=hash_password(user_data.password),
        full_name=user_data.full_name
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return user


@router.post('/login', response_model=TokenResponse, dependencies=[Depends(rate_limit_login)])
def login(login_data: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == login_data.email).first()
    if not user or not verify_password(login_data.password, user.password_hash):
        raise InvalidCredentialsException()

    if not user.is_active:
        raise AccountLockedException()

    access_token = create_access_token({'sub': str(user.id)})
    refresh_token = create_refresh_token({'sub': str(user.id)})
    return TokenResponse(access_token=access_token, refresh_token=refresh_token)

@router.post('/refresh', response_model=AccessTokenResponse)
def refresh_access_token(payload: RefreshRequest, db: Session = Depends(get_db)):
    data = decode_access_token(payload.refresh_token)
    if not data or data.get('type') != 'refresh' or not data.get('sub'):
        raise InvalidRefreshTokenException()

    try:
        user_id = int(data['sub'])
    except (TypeError, ValueError):
        raise InvalidRefreshTokenException()

    user = db.query(User).filter(User.id == user_id).first()
    if not user or not user.is_active:
        raise InvalidRefreshTokenException()
    
    if user.role != "ADMIN":
        raise AdminRequiredException()
    
    new_access_token = create_access_token({'sub': str(user.id)})
    return AccessTokenResponse(access_token=new_access_token)