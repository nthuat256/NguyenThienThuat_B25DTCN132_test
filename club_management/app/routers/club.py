from datetime import datetime, timedelta, timezone
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import case
from sqlalchemy.orm import Session, joinedload

from app.core.exception import (
    ClubMemberRequiredException, ClubNotFoundException, ClubOwnerRequiredException,
    UserAlreadyMemberException, UserNotFoundException,
)
from app.db.database import get_db
from app.dependencies import get_current_user
from app.models.club import Club, ClubMember
from app.models.user import User
from app.schemas.club import (
    ClubCreate, ClubDetailResponse, ClubMemberCreate, ClubMemberResponse,
    ClubMemberRoleUpdate, ClubResponse, ClubUpdate, OwnerInfo,
)

router = APIRouter(prefix="/clubs", tags=["clubs"])


def get_club(club_id: int, db: Session) -> Club:
    club = db.query(Club).filter(Club.id == club_id, Club.is_deleted.is_(False)).first()
    if not club:
        raise ClubNotFoundException()
    return club


def get_membership(club_id: int, user_id: int, db: Session) -> ClubMember | None:
    return db.query(ClubMember).filter(ClubMember.club_id == club_id, ClubMember.user_id == user_id).first()


@router.post("", response_model=ClubResponse, status_code=status.HTTP_201_CREATED)
def create_club(club_data: ClubCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    owner_count = db.query(Club).filter(Club.owner_id == current_user.id, Club.is_deleted.is_(False)).count()
    if owner_count >= 5:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Mỗi user chỉ được tạo tối đa 5 chiến dịch")

    data = club_data.model_dump()
    data["name"] = data["name"].title()
    
    club = Club(**data, owner_id=current_user.id)
    db.add(club)
    db.flush()

    owner_member = ClubMember(club_id=club.id, user_id=current_user.id, role="OWNER")
    db.add(owner_member)
    db.commit()
    db.refresh(club)

    return club


@router.get("", response_model=list[ClubResponse])
def get_clubs(search: str | None = None, role: str | None = None, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    query = db.query(Club).join(ClubMember, ClubMember.club_id == Club.id).filter(
        ClubMember.user_id == current_user.id, Club.is_deleted.is_(False)
    )

    if search:
        query = query.filter(Club.name.ilike(f"%{search.strip()}%"))

    if role:
        if role not in ["OWNER", "MEMBER", "VIEWER"]:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Role không hợp lệ")
        query = query.filter(ClubMember.role == role)

    return query.order_by(Club.name.asc()).all()


@router.get("/{club_id}", response_model=ClubDetailResponse)
def get_club_by_id(club_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    club = get_club(club_id, db)
    
    membership = get_membership(club_id, current_user.id, db)
    if not membership:
        raise ClubMemberRequiredException()

    total_members = db.query(ClubMember).filter(ClubMember.club_id == club_id).count()
    owner = db.query(User).filter(User.id == club.owner_id).first()

    return {
        "id": club.id,
        "name": club.name,
        "description": club.description,
        "owner_id": club.owner_id,
        "created_at": club.created_at,
        "total_members": total_members,
        "owner_info": {
            "id": owner.id,
            "full_name": owner.full_name,
            "email": owner.email,
        },
    }


@router.patch("/{club_id}", response_model=ClubResponse)
def update_club(club_id: int, club_data: ClubUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    club = get_club(club_id, db)

    if club.owner_id != current_user.id:
        raise ClubOwnerRequiredException("cập nhật câu lạc bộ")

    update_data = club_data.model_dump(exclude_unset=True)
    if not update_data:
        return club

    if "name" in update_data:
        now = datetime.now(timezone.utc)
        created_at = club.created_at
        
        if created_at.tzinfo is None:
            created_at = created_at.replace(tzinfo=timezone.utc)

        if now - created_at > timedelta(days=7):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Không thể sửa tên sau 7 ngày kể từ khi tạo")

        update_data["name"] = update_data["name"].title()

    for key, value in update_data.items():
        setattr(club, key, value)

    db.commit()
    db.refresh(club)
    
    return club


@router.delete("/{club_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_club(club_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    club = get_club(club_id, db)

    if club.owner_id != current_user.id:
        raise ClubOwnerRequiredException("xóa câu lạc bộ")

    member_count = db.query(ClubMember).filter(ClubMember.club_id == club_id).count()
    if member_count > 3:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cần xóa bớt thành viên trước")

    club.is_deleted = True
    club.deleted_at = datetime.now(timezone.utc)
    db.commit()


@router.post("/{club_id}/members", response_model=ClubMemberResponse, status_code=status.HTTP_201_CREATED)
def add_member(club_id: int, member_data: ClubMemberCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    club = get_club(club_id, db)
    current_membership = get_membership(club_id, current_user.id, db)

    if not current_membership:
        raise ClubMemberRequiredException()

    if current_membership.role not in ["OWNER", "MEMBER"]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Bạn không có quyền thêm thành viên")

    if member_data.user_id == current_user.id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Bạn đã là thành viên trong nhóm")

    user = db.query(User).filter(User.id == member_data.user_id).first()
    if not user:
        raise UserNotFoundException()

    existing_member = get_membership(club_id, member_data.user_id, db)
    if existing_member:
        raise UserAlreadyMemberException()

    member_count = db.query(ClubMember).filter(ClubMember.club_id == club_id).count()
    if member_count >= 10:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Đã đạt tối đa 10 thành viên")

    member = ClubMember(club_id=club_id, user_id=member_data.user_id, role=member_data.role)
    db.add(member)
    db.commit()
    db.refresh(member)
    
    return member


@router.get("/{club_id}/members", response_model=list[ClubMemberResponse])
def get_members(club_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    club = get_club(club_id, db)
    current_membership = get_membership(club_id, current_user.id, db)

    if not current_membership:
        raise ClubMemberRequiredException()

    return (
        db.query(ClubMember)
        .filter(ClubMember.club_id == club.id)
        .order_by(
            case((ClubMember.role == "OWNER", 0), else_=1),
            ClubMember.joined_at.asc(),
        )
        .all()
    )


@router.delete("/{club_id}/members/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_member(club_id: int, user_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    club = get_club(club_id, db)
    current_membership = get_membership(club_id, current_user.id, db)

    if not current_membership:
        raise ClubMemberRequiredException()

    target_member = get_membership(club_id, user_id, db)
    if not target_member:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Không tìm thấy thành viên")

    if current_user.id == user_id:
        if current_membership.role == "OWNER":
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Owner không thể tự rời nhóm")
        db.delete(target_member)
        db.commit()
        return

    if current_membership.role != "OWNER":
        raise ClubOwnerRequiredException("xóa thành viên")

    if target_member.role == "OWNER":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Không thể xóa Owner")

    db.delete(target_member)
    db.commit()


@router.patch("/{club_id}/members/{user_id}/role", response_model=ClubMemberResponse)
def update_member_role(club_id: int, user_id: int, role_data: ClubMemberRoleUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    club = get_club(club_id, db)

    if club.owner_id != current_user.id:
        raise ClubOwnerRequiredException("đổi role thành viên")

    member = get_membership(club_id, user_id, db)
    if not member:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Không tìm thấy thành viên")

    if member.role == "OWNER":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Không thể đổi role của Owner")

    member.role = role_data.role
    db.commit()
    db.refresh(member)
    
    return member