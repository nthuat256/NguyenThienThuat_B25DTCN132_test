# FastAPI Club Management

API quản lý câu lạc bộ, thành viên và hoạt động với FastAPI, SQLAlchemy và JWT Authentication.

## Chức năng

- Đăng ký, đăng nhập và xác thực JWT.
- Phân quyền ADMIN/USER và kiểm tra quyền theo owner/member của câu lạc bộ.
- CRUD câu lạc bộ.
- Soft delete câu lạc bộ.
- Thêm và xem thành viên câu lạc bộ.
- CRUD hoạt động của câu lạc bộ.
- Giao activity cho thành viên trong cùng câu lạc bộ.
- Search, filter, pagination và sort activity.
- Pagination và search danh sách club/user.
- Custom HTTP exception.
- Login rate limiting.
- Pytest + FastAPI TestClient.

## Công nghệ

- Python
- FastAPI
- Uvicorn
- SQLAlchemy
- SQLite cho môi trường mặc định/test
- MySQL + PyMySQL cho môi trường triển khai
- Pydantic
- PyJWT
- Bcrypt
- Python Dotenv
- Pytest
- HTTPX

## Cấu trúc

```text
club_management/
├── app/
│   ├── core/
│   │   ├── config.py
│   │   ├── exception.py
│   │   ├── rate_limit.py
│   │   └── security.py
│   ├── db/
│   │   ├── database.py
│   │   └── seed.py
│   ├── models/
│   │   ├── activity.py
│   │   ├── club.py
│   │   └── user.py
│   ├── routers/
│   │   ├── activity.py
│   │   ├── auth.py
│   │   ├── club.py
│   │   └── users.py
│   ├── schemas/
│   │   ├── activity.py
│   │   ├── club.py
│   │   └── user.py
│   ├── test/
│   │   ├── conftest.py
│   │   ├── test_activity.py
│   │   ├── test_club.py
│   │   └── test_user.py
│   ├── dependencies.py
│   └── main.py
├── .env.example
├── .gitignore
└── requirements.txt
```

## Cài đặt

```bash
cd club_management
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

Linux/macOS:

```bash
source .venv/bin/activate
pip install -r requirements.txt
```

## Cấu hình

Tạo `.env` từ `.env.example` và thay các giá trị phù hợp với môi trường chạy.

Database mặc định:

```text
sqlite:///./club_management.db
```

Có thể đổi `DATABASE_URL` sang MySQL khi triển khai.

## Seed dữ liệu

Sau khi cấu hình database:

```bash
python -m app.db.seed
```

Nếu cần dữ liệu mẫu cho test, test suite cũng tự gọi `seed_data()`.

Tài khoản seed mặc định:

```text
ADMIN
email: admin@gmail.com
password: 123456

USER
email: nguyenvana@gmail.com
password: 123456
```

Không sử dụng mật khẩu mẫu này trong môi trường thật.

## Chạy API

```bash
uvicorn app.main:app --reload
```

Swagger:

```text
http://127.0.0.1:8000/docs
```

ReDoc:

```text
http://127.0.0.1:8000/redoc
```

Health check:

```text
GET /health
```

## Activity API

Collection:

```text
POST /clubs/{club_id}/activities
GET  /clubs/{club_id}/activities
```

Detail:

```text
GET    /activities/{activity_id}
PATCH  /activities/{activity_id}
DELETE /activities/{activity_id}
```

Danh sách activity hỗ trợ:

```text
search
status
priority
assignee_id
limit
offset
sort_by = created_at | due_date | title
sort_order = asc | desc
```

## Club API

```text
POST   /clubs
GET    /clubs
GET    /clubs/{club_id}
PUT    /clubs/{club_id}
DELETE /clubs/{club_id}

POST /clubs/{club_id}/members
GET  /clubs/{club_id}/members
```

## User API

```text
GET /users/me
GET /users
```

`GET /users` dành cho ADMIN và hỗ trợ search, limit, offset.

## Test

Chạy toàn bộ test:

```bash
pytest -q
```

Test tập trung vào:

- CRUD.
- Permission và ownership.
- Member validation.
- Activity assignee validation.
- Search/filter/pagination/sort.
- Soft delete.
- Request validation.
- User listing và permission.

## Lưu ý

Database runtime (`*.db`, `*.sqlite`, `*.sqlite3`), `.env` và cache Python không được commit vào Git.