from datetime import datetime, timedelta, timezone

from app.core.security import get_password_hash
from app.db.database import SessionLocal
from app.models.activity import ClubActivity
from app.models.club import Club, ClubLog, ClubMember
from app.models.user import User


def get_or_create(db, model, filter_by: dict, **kwargs):
    instance = db.query(model).filter_by(**filter_by).first()
    if instance:
        return instance

    instance = model(**{**filter_by, **kwargs})
    db.add(instance)
    db.commit()
    db.refresh(instance)
    return instance


def seed_data():
    with SessionLocal() as db:
        now = datetime.now(timezone.utc)

        users_data = [
            {
                "email": "admin@gmail.com",
                "full_name": "System Admin",
                "role": "ADMIN",
                "is_active": True,
            },
            {
                "email": "admin2@gmail.com",
                "full_name": "Backup Admin",
                "role": "ADMIN",
                "is_active": True,
            },
            {
                "email": "nguyenvana@gmail.com",
                "full_name": "Nguyen Van A",
                "role": "USER",
                "is_active": True,
            },
            {
                "email": "nguyenvanb@gmail.com",
                "full_name": "Nguyen Van B",
                "role": "USER",
                "is_active": True,
            },
            {
                "email": "tranthib@gmail.com",
                "full_name": "Tran Thi B",
                "role": "USER",
                "is_active": True,
            },
            {
                "email": "levanc@gmail.com",
                "full_name": "Le Van C",
                "role": "USER",
                "is_active": True,
            },
            {
                "email": "phamthid@gmail.com",
                "full_name": "Pham Thi D",
                "role": "USER",
                "is_active": True,
            },
            {
                "email": "hoangminhe@gmail.com",
                "full_name": "Hoang Minh E",
                "role": "USER",
                "is_active": True,
            },
            {
                "email": "inactive.user@gmail.com",
                "full_name": "Inactive User",
                "role": "USER",
                "is_active": False,
            },
            {
                "email": "inactive.owner@gmail.com",
                "full_name": "Inactive Owner",
                "role": "USER",
                "is_active": False,
            },
            {
                "email": "lonely.user@gmail.com",
                "full_name": "Lonely User",
                "role": "USER",
                "is_active": True,
            },
        ]

        users = {}
        for user_data in users_data:
            email = user_data["email"]
            users[email] = get_or_create(
                db,
                User,
                {"email": email},
                password_hash=get_password_hash("123456"),
                full_name=user_data["full_name"],
                role=user_data["role"],
                is_active=user_data["is_active"],
            )

        admin = users["admin@gmail.com"]
        admin2 = users["admin2@gmail.com"]
        user_a = users["nguyenvana@gmail.com"]
        user_b = users["nguyenvanb@gmail.com"]
        user_c = users["tranthib@gmail.com"]
        user_d = users["levanc@gmail.com"]
        user_e = users["phamthid@gmail.com"]
        user_f = users["hoangminhe@gmail.com"]
        inactive_user = users["inactive.user@gmail.com"]
        inactive_owner = users["inactive.owner@gmail.com"]

        clubs_data = [
    # CLUB 1
    # Owner: admin@gmail.com
    {
        "name": "Python Club",
        "description": "Cau lac bo lap trinh Python va FastAPI",
        "owner_id": admin.id,
        "is_deleted": False,
        "deleted_at": None,
    },

    # CLUB 2
    # Owner: nguyenvana@gmail.com
    {
        "name": "Web Development Club",
        "description": "Cau lac bo phat trien ung dung Web",
        "owner_id": user_a.id,
        "is_deleted": False,
        "deleted_at": None,
    },

    # CLUB 3
    # Owner: tranthib@gmail.com
    {
        "name": "Data Science Club",
        "description": "Cau lac bo Data Analysis va Machine Learning",
        "owner_id": user_c.id,
        "is_deleted": False,
        "deleted_at": None,
    },

    # CLUB 4
    # Chỉ có owner, không có Activity
    {
        "name": "Empty Club",
        "description": "Club chi co owner va khong co activity",
        "owner_id": user_f.id,
        "is_deleted": False,
        "deleted_at": None,
    },

    # CLUB 5
    # Club tối thiểu
    {
        "name": "Minimal Club",
        "description": None,
        "owner_id": user_e.id,
        "is_deleted": False,
        "deleted_at": None,
    },

    # CLUB 6
    # Owner + 1 member
    {
        "name": "Small Club",
        "description": "Club chi co owner va mot member",
        "owner_id": user_b.id,
        "is_deleted": False,
        "deleted_at": None,
    },

    # CLUB 7
    # Owner inactive
    {
        "name": "Inactive Owner Club",
        "description": "Club du lieu co owner inactive",
        "owner_id": inactive_owner.id,
        "is_deleted": False,
        "deleted_at": None,
    },

    # CLUB 8
    # Soft deleted
    {
        "name": "Deleted Club",
        "description": "Club dung de test soft delete",
        "owner_id": admin2.id,
        "is_deleted": True,
        "deleted_at": now - timedelta(days=7),
    },
]
        

        clubs = {}
        for club_data in clubs_data:
            name = club_data["name"]
            club = get_or_create(
                db,
                Club,
                {"name": name},
                description=club_data["description"],
                owner_id=club_data["owner_id"],
                is_deleted=club_data["is_deleted"],
                deleted_at=club_data["deleted_at"],
            )

            club.description = club_data["description"]
            club.owner_id = club_data["owner_id"]
            club.is_deleted = club_data["is_deleted"]
            club.deleted_at = club_data["deleted_at"]
            db.commit()
            db.refresh(club)
            clubs[name] = club

        python_club = clubs["Python Club"]
        web_club = clubs["Web Development Club"]
        data_club = clubs["Data Science Club"]
        empty_club = clubs["Empty Club"]
        minimal_club = clubs["Minimal Club"]
        small_club = clubs["Small Club"]
        inactive_owner_club = clubs["Inactive Owner Club"]
        deleted_club = clubs["Deleted Club"]

        members_data = [
            # CLUB 1 - Python Club
            (python_club.id, admin.id, "OWNER"),
            (python_club.id, user_a.id, "MEMBER"),
            (python_club.id, user_b.id, "MODERATOR"),
            (python_club.id, user_c.id, "MEMBER"),
            (python_club.id, user_d.id, "MEMBER"),
            (python_club.id, inactive_user.id, "MEMBER"),
            # CLUB 2 - Web Development Club
            (web_club.id, user_a.id, "OWNER"),
            (web_club.id, user_b.id, "MEMBER"),
            (web_club.id, user_c.id, "MODERATOR"),
            (web_club.id, user_d.id, "MEMBER"),
            (web_club.id, admin.id, "MEMBER"),
            # CLUB 3 - Data Science Club
            (data_club.id, user_c.id, "OWNER"),
            (data_club.id, user_a.id, "MEMBER"),
            (data_club.id, user_b.id, "MODERATOR"),
            (data_club.id, user_d.id, "MEMBER"),
            (data_club.id, user_e.id, "MEMBER"),
            (data_club.id, admin.id, "MEMBER"),
            # CLUB 4 - Empty Club
            (empty_club.id, user_f.id, "OWNER"),
            # CLUB 5 - Minimal Club
            (minimal_club.id, user_e.id, "OWNER"),
            # CLUB 6 - Small Club
            (small_club.id, user_b.id, "OWNER"),
            (small_club.id, user_d.id, "MEMBER"),
            # CLUB 7 - Inactive Owner Club
            (inactive_owner_club.id, inactive_owner.id, "OWNER"),
            (inactive_owner_club.id, user_a.id, "MEMBER"),
            # CLUB 8 - Deleted Club
            (deleted_club.id, admin2.id, "OWNER"),
            (deleted_club.id, user_a.id, "MEMBER"),
        ]

        for club_id, user_id, role in members_data:
            get_or_create(
                db,
                ClubMember,
                {"club_id": club_id, "user_id": user_id},
                role=role,
            )

        activities_data = [
            {
                "club_id": python_club.id,
                "title": "FastAPI Workshop",
                "description": "Buoi hoc FastAPI co ban",
                "status": "TODO",
                "priority": "HIGH",
                "assignee_id": user_a.id,
                "due_date": now + timedelta(days=7),
            },
            {
                "club_id": python_club.id,
                "title": "Python Basic Practice",
                "description": "On tap Python co ban cho thanh vien moi",
                "status": "IN_PROGRESS",
                "priority": "MEDIUM",
                "assignee_id": user_b.id,
                "due_date": now + timedelta(days=3),
            },
            {
                "club_id": python_club.id,
                "title": "Build CRUD API",
                "description": "Thuc hanh CRUD API voi FastAPI va SQLAlchemy",
                "status": "DONE",
                "priority": "HIGH",
                "assignee_id": user_c.id,
                "due_date": now - timedelta(days=2),
            },
            {
                "club_id": python_club.id,
                "title": "Optional Task Without Assignee",
                "description": "Dung de test assignee_id = null",
                "status": "TODO",
                "priority": "LOW",
                "assignee_id": None,
                "due_date": None,
            },
            {
                "club_id": python_club.id,
                "title": "Todo Overdue Task",
                "description": "TODO nhung da qua han",
                "status": "TODO",
                "priority": "HIGH",
                "assignee_id": user_d.id,
                "due_date": now - timedelta(days=1),
            },
            {
                "club_id": python_club.id,
                "title": "In Progress Overdue Task",
                "description": "IN_PROGRESS nhung da qua han",
                "status": "IN_PROGRESS",
                "priority": "MEDIUM",
                "assignee_id": user_a.id,
                "due_date": now - timedelta(hours=6),
            },
            {
                "club_id": python_club.id,
                "title": "Due Today Task",
                "description": "Activity den han trong ngay hom nay",
                "status": "TODO",
                "priority": "MEDIUM",
                "assignee_id": user_b.id,
                "due_date": now + timedelta(hours=4),
            },
            {
                "club_id": python_club.id,
                "title": "Due Soon Task",
                "description": "Activity sap het han",
                "status": "IN_PROGRESS",
                "priority": "HIGH",
                "assignee_id": user_c.id,
                "due_date": now + timedelta(hours=1),
            },
            {
                "club_id": web_club.id,
                "title": "HTML CSS Workshop",
                "description": "Thuc hanh giao dien Web co ban",
                "status": "TODO",
                "priority": "MEDIUM",
                "assignee_id": user_b.id,
                "due_date": now + timedelta(days=5),
            },
            {
                "club_id": web_club.id,
                "title": "JavaScript Practice",
                "description": "Thuc hanh JavaScript va xu ly DOM",
                "status": "IN_PROGRESS",
                "priority": "HIGH",
                "assignee_id": user_c.id,
                "due_date": now + timedelta(days=1),
            },
            {
                "club_id": web_club.id,
                "title": "Responsive UI Finished",
                "description": "Hoan thanh giao dien responsive",
                "status": "DONE",
                "priority": "LOW",
                "assignee_id": user_d.id,
                "due_date": now - timedelta(days=5),
            },
            {
                "club_id": web_club.id,
                "title": "Same Title",
                "description": "Dung de test trung title giua cac club",
                "status": "TODO",
                "priority": "LOW",
                "assignee_id": user_b.id,
                "due_date": None,
            },
            {
                "club_id": data_club.id,
                "title": "Data Analysis Workshop",
                "description": "Lam quen voi Pandas va xu ly du lieu",
                "status": "TODO",
                "priority": "HIGH",
                "assignee_id": user_e.id,
                "due_date": now + timedelta(days=10),
            },
            {
                "club_id": data_club.id,
                "title": "SQL Practice",
                "description": "Thuc hanh SELECT JOIN GROUP BY va HAVING",
                "status": "DONE",
                "priority": "MEDIUM",
                "assignee_id": user_d.id,
                "due_date": now - timedelta(days=1),
            },
            {
                "club_id": data_club.id,
                "title": "ML Discussion",
                "description": None,
                "status": "IN_PROGRESS",
                "priority": "LOW",
                "assignee_id": admin.id,
                "due_date": None,
            },
            {
                "club_id": data_club.id,
                "title": "Same Title",
                "description": "Cung title voi Web Club nhung khac club_id",
                "status": "DONE",
                "priority": "MEDIUM",
                "assignee_id": user_a.id,
                "due_date": now + timedelta(days=3),
            },
            {
                "club_id": data_club.id,
                "title": "Finished Early",
                "description": "DONE nhung due_date van o tuong lai",
                "status": "DONE",
                "priority": "HIGH",
                "assignee_id": user_b.id,
                "due_date": now + timedelta(days=4),
            },
        ]

        for activity_data in activities_data:
            get_or_create(
                db,
                ClubActivity,
                {
                    "club_id": activity_data["club_id"],
                    "title": activity_data["title"],
                },
                description=activity_data["description"],
                status=activity_data["status"],
                priority=activity_data["priority"],
                assignee_id=activity_data["assignee_id"],
                due_date=activity_data["due_date"],
            )

        logs_data = [
            (python_club.id, admin.id, "CREATE_CLUB"),
            (python_club.id, admin.id, "ADD_MEMBER"),
            (python_club.id, user_a.id, "CREATE_ACTIVITY"),
            (web_club.id, user_a.id, "CREATE_CLUB"),
            (web_club.id, user_c.id, "UPDATE_ACTIVITY"),
            (data_club.id, user_c.id, "CREATE_CLUB"),
            (data_club.id, user_a.id, "COMPLETE_ACTIVITY"),
            (deleted_club.id, admin2.id, "CREATE_CLUB"),
            (deleted_club.id, admin2.id, "DELETE_CLUB"),
            (inactive_owner_club.id, inactive_owner.id, "CREATE_CLUB"),
        ]

        for club_id, user_id, action in logs_data:
            get_or_create(
                db,
                ClubLog,
                {
                    "club_id": club_id,
                    "user_id": user_id,
                    "action": action,
                },
            )

        print("Da seed du lieu mau thanh cong!")
        print("Mat khau tat ca tai khoan: 123456")
        print("ADMIN: admin@gmail.com, admin2@gmail.com")
        print("USER ACTIVE: nguyenvana@gmail.com, nguyenvanb@gmail.com, tranthib@gmail.com")
        print("USER ACTIVE: levanc@gmail.com, phamthid@gmail.com, hoangminhe@gmail.com")
        print("USER INACTIVE: inactive.user@gmail.com, inactive.owner@gmail.com")
        print("USER KHONG THAM GIA CLUB: lonely.user@gmail.com")


if __name__ == "__main__":
    seed_data()