from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.core.exception import (
    ActivityAssigneeNotMemberException,
    ActivityNotFoundException,
    ActivityPermissionException,
    ClubMemberRequiredException,
    ClubNotFoundException,
)
from app.db.database import get_db
from app.dependencies import get_current_user
from app.models.activity import ClubActivity
from app.models.club import Club, ClubMember
from app.models.user import User
from app.schemas.activity import (
    ActivityCreate,
    ActivityPriority,
    ActivityResponse,
    ActivityStatus,
    ActivityUpdate,
)

club_activity_router = APIRouter(
    prefix="/clubs/{club_id}/activities",
    tags=["activities"],
)

activity_router = APIRouter(prefix="/activities", tags=["activities"])


def get_club(club_id: int, db: Session) -> Club:
    club = db.query(Club).filter(Club.id == club_id).first()
    if not club or club.is_deleted:
        raise ClubNotFoundException()
    return club


def get_membership(club_id: int, user_id: int, db: Session) -> ClubMember:
    member = (
        db.query(ClubMember)
        .filter(
            ClubMember.club_id == club_id,
            ClubMember.user_id == user_id,
        )
        .first()
    )
    if not member:
        raise ClubMemberRequiredException()
    return member


def get_activity(activity_id: int, db: Session) -> ClubActivity:
    activity = db.query(ClubActivity).filter(ClubActivity.id == activity_id).first()
    if not activity:
        raise ActivityNotFoundException()
    return activity


def validate_assignee(club_id: int, assignee_id: int | None, db: Session) -> None:
    if assignee_id is None:
        return

    member = (
        db.query(ClubMember)
        .filter(
            ClubMember.club_id == club_id,
            ClubMember.user_id == assignee_id,
        )
        .first()
    )
    if not member:
        raise ActivityAssigneeNotMemberException()


def check_update_permission(
    activity: ClubActivity,
    current_user: User,
    db: Session,
) -> ClubMember:
    member = get_membership(activity.club_id, current_user.id, db)
    if member.role == "OWNER" or activity.assignee_id == current_user.id:
        return member
    raise ActivityPermissionException("cập nhật")


@club_activity_router.post(
    "",
    response_model=ActivityResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Tạo hoạt động câu lạc bộ",
)
def create_activity(
    club_id: int,
    activity_data: ActivityCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    get_club(club_id, db)
    get_membership(club_id, current_user.id, db)
    validate_assignee(club_id, activity_data.assignee_id, db)

    activity = ClubActivity(club_id=club_id, **activity_data.model_dump())
    db.add(activity)
    db.commit()
    db.refresh(activity)
    return activity


@club_activity_router.get(
    "",
    response_model=list[ActivityResponse],
    summary="Danh sách hoạt động",
)
def get_activities(
    club_id: int,
    search: str | None = Query(None, min_length=1, max_length=255),
    status: ActivityStatus | None = Query(None),
    priority: ActivityPriority | None = Query(None),
    assignee_id: int | None = Query(None, ge=1),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    sort_by: str = Query("created_at", pattern="^(created_at|due_date|title)$"),
    sort_order: str = Query("desc", pattern="^(asc|desc)$"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    get_club(club_id, db)
    get_membership(club_id, current_user.id, db)

    query = db.query(ClubActivity).filter(ClubActivity.club_id == club_id)

    if search:
        query = query.filter(ClubActivity.title.ilike(f"%{search.strip()}%"))
    if status:
        query = query.filter(ClubActivity.status == status)
    if priority:
        query = query.filter(ClubActivity.priority == priority)
    if assignee_id is not None:
        query = query.filter(ClubActivity.assignee_id == assignee_id)

    sort_column = {
        "created_at": ClubActivity.created_at,
        "due_date": ClubActivity.due_date,
        "title": ClubActivity.title,
    }[sort_by]

    query = query.order_by(
        sort_column.asc() if sort_order == "asc" else sort_column.desc()
    )

    return query.offset(offset).limit(limit).all()


@activity_router.get(
    "/{activity_id}",
    response_model=ActivityResponse,
    summary="Xem chi tiết hoạt động",
)
def get_activity_by_id(
    activity_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    activity = get_activity(activity_id, db)
    get_club(activity.club_id, db)
    get_membership(activity.club_id, current_user.id, db)
    return activity


@activity_router.patch(
    "/{activity_id}",
    response_model=ActivityResponse,
    summary="Cập nhật hoạt động",
)
def update_activity(
    activity_id: int,
    activity_data: ActivityUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    activity = get_activity(activity_id, db)
    get_club(activity.club_id, db)
    member = check_update_permission(activity, current_user, db)

    data = activity_data.model_dump(exclude_unset=True)

    if not data:
        return activity

    if member.role != "OWNER" and "assignee_id" in data:
        raise ActivityPermissionException("thay đổi assignee của")

    if "assignee_id" in data:
        validate_assignee(activity.club_id, data["assignee_id"], db)

    for key, value in data.items():
        setattr(activity, key, value)

    db.commit()
    db.refresh(activity)
    return activity


@activity_router.delete(
    "/{activity_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Xóa hoạt động",
)
def delete_activity(
    activity_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    activity = get_activity(activity_id, db)
    get_club(activity.club_id, db)
    member = get_membership(activity.club_id, current_user.id, db)

    if member.role != "OWNER":
        raise ActivityPermissionException("xóa")

    db.delete(activity)
    db.commit()