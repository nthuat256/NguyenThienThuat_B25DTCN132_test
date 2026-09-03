import bcrypt
import jwt
from datetime import datetime, timedelta, timezone
from app.core.config import (
    ACCESS_TOKEN_EXPIRE_MINUTES,
    ALGORITHM,
    REFRESH_TOKEN_EXPIRE_DAYS,
    SECRET_KEY,
)

def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode()[:72], bcrypt.gensalt()).decode()

def get_password_hash(password: str) -> str:
    return hash_password(password)

def verify_password(password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(password.encode()[:72], hashed_password.encode())

def _create_token(data: dict, expires_delta: timedelta, token_type: str) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + expires_delta
    to_encode.update({"exp": expire, "type": token_type})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def create_access_token(data: dict) -> str:
    return _create_token(
        data, timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES), "access"
    )

def create_refresh_token(data: dict) -> str:
    return _create_token(
        data, timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS), "refresh"
    )

def decode_access_token(token: str):
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except jwt.PyJWTError:
        return None