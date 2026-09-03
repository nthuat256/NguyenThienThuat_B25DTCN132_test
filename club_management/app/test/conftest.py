import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

ROOT_DIR = Path(__file__).resolve().parents[2]

if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from app.db.seed import seed_data
from app.main import app


@pytest.fixture(scope="session", autouse=True)
def seed_test_data():
    seed_data()


@pytest.fixture
def client():
    with TestClient(app) as test_client:
        yield test_client


def login(client, email, password="123456"):
    response = client.post(
        "/auth/login",
        json={
            "email": email,
            "password": password,
        },
    )
    assert response.status_code == 200, response.text
    return response.json()["access_token"]


@pytest.fixture
def admin_token(client):
    return login(client, "admin@gmail.com")


@pytest.fixture
def user_token(client):
    return login(client, "nguyenvana@gmail.com")


def auth_header(token):
    return {"Authorization": f"Bearer {token}"}