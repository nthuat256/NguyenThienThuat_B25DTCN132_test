from conftest import auth_header


def test_get_current_user(client, admin_token):
    response = client.get("/users/me", headers=auth_header(admin_token))
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "admin@gmail.com"
    assert data["role"] == "ADMIN"


def test_admin_can_list_users(client, admin_token):
    response = client.get(
        "/users",
        headers=auth_header(admin_token),
        params={"limit": 10, "offset": 0},
    )
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_admin_can_search_users(client, admin_token):
    response = client.get(
        "/users",
        headers=auth_header(admin_token),
        params={"search": "nguyenvana@gmail.com"},
    )
    assert response.status_code == 200
    assert any(item["email"] == "nguyenvana@gmail.com" for item in response.json())


def test_non_admin_cannot_list_users(client, user_token):
    response = client.get("/users", headers=auth_header(user_token))
    assert response.status_code == 403


def test_invalid_user_pagination(client, admin_token):
    response = client.get(
        "/users",
        headers=auth_header(admin_token),
        params={"limit": 101},
    )
    assert response.status_code == 422