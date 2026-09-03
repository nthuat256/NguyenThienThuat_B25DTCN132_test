import uuid

from conftest import auth_header


def create_club(client, token, **overrides):
    payload = {
        "name": f"Club Test {uuid.uuid4().hex}",
        "description": "Automated test",
    }
    payload.update(overrides)
    response = client.post(
        "/clubs",
        headers=auth_header(token),
        json=payload,
    )
    assert response.status_code == 201, response.text
    return response.json()


def get_non_admin_user_id(client, admin_token):
    response = client.get(
        "/users",
        headers=auth_header(admin_token),
        params={"limit": 100},
    )
    assert response.status_code == 200, response.text
    users = response.json()
    user = next(item for item in users if item["role"] != "ADMIN")
    return user["id"]


def test_create_club(client, admin_token):
    club = create_club(client, admin_token)
    assert club["id"] > 0
    assert club["name"].startswith("Club Test")


def test_get_clubs_with_search_and_pagination(client, admin_token):
    club = create_club(client, admin_token, name="Unique Search Club")
    response = client.get(
        "/clubs",
        headers=auth_header(admin_token),
        params={"search": "Unique Search", "limit": 1, "offset": 0},
    )
    assert response.status_code == 200
    assert any(item["id"] == club["id"] for item in response.json())


def test_get_club_by_id(client, admin_token):
    club = create_club(client, admin_token)
    response = client.get(
        f"/clubs/{club['id']}",
        headers=auth_header(admin_token),
    )
    assert response.status_code == 200
    assert response.json()["id"] == club["id"]


def test_update_club(client, admin_token):
    club = create_club(client, admin_token)
    response = client.put(
        f"/clubs/{club['id']}",
        headers=auth_header(admin_token),
        json={"name": "Updated Club", "description": "Updated"},
    )
    assert response.status_code == 200
    assert response.json()["name"] == "Updated Club"


def test_update_club_empty_body(client, admin_token):
    club = create_club(client, admin_token)
    response = client.put(
        f"/clubs/{club['id']}",
        headers=auth_header(admin_token),
        json={},
    )
    assert response.status_code == 200
    assert response.json()["id"] == club["id"]


def test_delete_club_is_soft_delete(client, admin_token):
    club = create_club(client, admin_token)
    response = client.delete(
        f"/clubs/{club['id']}",
        headers=auth_header(admin_token),
    )
    assert response.status_code == 204

    response = client.get(
        f"/clubs/{club['id']}",
        headers=auth_header(admin_token),
    )
    assert response.status_code == 404


def test_user_cannot_update_or_delete_other_users_club(client, admin_token, user_token):
    club = create_club(client, admin_token)

    response = client.put(
        f"/clubs/{club['id']}",
        headers=auth_header(user_token),
        json={"name": "Unauthorized"},
    )
    assert response.status_code == 403

    response = client.delete(
        f"/clubs/{club['id']}",
        headers=auth_header(user_token),
    )
    assert response.status_code == 403


def test_user_cannot_view_other_users_club(client, admin_token, user_token):
    club = create_club(client, admin_token)
    response = client.get(
        f"/clubs/{club['id']}",
        headers=auth_header(user_token),
    )
    assert response.status_code == 403


def test_add_member_and_duplicate_member(client, admin_token):
    club = create_club(client, admin_token)
    user_id = get_non_admin_user_id(client, admin_token)

    response = client.post(
        f"/clubs/{club['id']}/members",
        headers=auth_header(admin_token),
        json={"user_id": user_id},
    )
    assert response.status_code == 201, response.text

    response = client.post(
        f"/clubs/{club['id']}/members",
        headers=auth_header(admin_token),
        json={"user_id": user_id},
    )
    assert response.status_code == 409


def test_non_owner_cannot_add_member(client, admin_token, user_token):
    club = create_club(client, admin_token)
    user_id = get_non_admin_user_id(client, admin_token)
    response = client.post(
        f"/clubs/{club['id']}/members",
        headers=auth_header(user_token),
        json={"user_id": user_id},
    )
    assert response.status_code == 403


def test_get_members(client, admin_token):
    club = create_club(client, admin_token)
    response = client.get(
        f"/clubs/{club['id']}/members",
        headers=auth_header(admin_token),
        params={"limit": 10, "offset": 0},
    )
    assert response.status_code == 200
    assert len(response.json()) >= 1


def test_invalid_club_payload(client, admin_token):
    response = client.post(
        "/clubs",
        headers=auth_header(admin_token),
        json={"name": ""},
    )
    assert response.status_code == 422


def test_invalid_pagination(client, admin_token):
    response = client.get(
        "/clubs",
        headers=auth_header(admin_token),
        params={"limit": 101},
    )
    assert response.status_code == 422


def test_missing_club(client, admin_token):
    response = client.get(
        "/clubs/999999999",
        headers=auth_header(admin_token),
    )
    assert response.status_code == 404