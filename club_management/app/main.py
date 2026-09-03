from fastapi import FastAPI, HTTPException
from fastapi import Depends
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.user import User

from app.core.exception import http_exception_handler
from app.db.database import Base, engine
from app.routers import auth, club as club_router, users
from app.routers.activity import activity_router, club_activity_router

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Student Club Management API",
    description="API quản lý câu lạc bộ, thành viên và hoạt động với JWT Authentication và phân quyền.",
    version="1.0.0",
)

app.add_exception_handler(HTTPException, http_exception_handler)
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(club_router.router)
app.include_router(club_activity_router)
app.include_router(activity_router)

@app.get("/health")
def health_check(db: Session = Depends(get_db)):

    return {
        "status": "healthy",
        "message":"wellcome"
    }