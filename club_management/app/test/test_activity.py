import uuid

from conftest import auth_header


def create_club(client, token):
    response = client.post(
        "/clubs",
        headers=auth_header(token),
        json={
            "name": f"Activity Test {uuid.uuid4().hex}",
            "description": "Test",
        },
    )
    assert response.status_code == 201, response.text
    return response.json()["id"]


def create_activity(client, token, club_id, **overrides):
    payload = {
        "title": f"Activity {uuid.uuid4().hex}",
        "description": "Automated test",
        "status": "TODO",
        "priority": "HIGH",
    }
    payload.update(overrides)

    response = client.post(
        f"/clubs/{club_id}/activities",
        headers=auth_header(token),
        json=payload,
    )
    assert response.status_code == 201, response.text
    return response.json()


def test_create_activity(client, admin_token):
    club_id = create_club(client, admin_token)
    activity = create_activity(client, admin_token, club_id)
    assert activity["club_id"] == club_id
    assert activity["status"] == "TODO"


def test_get_activities(client, admin_token):
    club_id = create_club(client, admin_token)
    create_activity(client, admin_token, club_id)
    response = client.get(
        f"/clubs/{club_id}/activities",
        headers=auth_header(admin_token),
    )
    assert response.status_code == 200
    assert len(response.json()) >= 1


def test_get_activity_by_id(client, admin_token):
    club_id = create_club(client, admin_token)
    activity = create_activity(client, admin_token, club_id)
    response = client.get(
        f"/activities/{activity['id']}",
        headers=auth_header(admin_token),
    )
    assert response.status_code == 200
    assert response.json()["id"] == activity["id"]


def test_update_activity(client, admin_token):
    club_id = create_club(client, admin_token)
    activity = create_activity(client, admin_token, club_id)
    response = client.patch(
        f"/activities/{activity['id']}",
        headers=auth_header(admin_token),
        json={"title": "Updated Activity", "status": "DONE", "priority": "LOW"},
    )
    assert response.status_code == 200
    assert response.json()["title"] == "Updated Activity"
    assert response.json()["status"] == "DONE"


def test_update_activity_empty_body_keeps_data(client, admin_token):
    club_id = create_club(client, admin_token)
    activity = create_activity(client, admin_token, club_id)
    response = client.patch(
        f"/activities/{activity['id']}",
        headers=auth_header(admin_token),
        json={},
    )
    assert response.status_code == 200
    assert response.json()["id"] == activity["id"]


def test_delete_activity(client, admin_token):
    club_id = create_club(client, admin_token)
    activity = create_activity(client, admin_token, club_id)
    response = client.delete(
        f"/activities/{activity['id']}",
        headers=auth_header(admin_token),
    )
    assert response.status_code == 204

    response = client.get(
        f"/activities/{activity['id']}",
        headers=auth_header(admin_token),
    )
    assert response.status_code == 404


def test_activity_requires_club_member(client, admin_token, user_token):
    club_id = create_club(client, admin_token)
    response = client.get(
        f"/clubs/{club_id}/activities",
        headers=auth_header(user_token),
    )
    assert response.status_code == 403


def test_create_activity_requires_club_member(client, admin_token, user_token):
    club_id = create_club(client, admin_token)
    response = client.post(
        f"/clubs/{club_id}/activities",
        headers=auth_header(user_token),
        json={"title": "Test"},
    )
    assert response.status_code == 403


def test_update_activity_requires_permission(client, admin_token, user_token):
    club_id = create_club(client, admin_token)
    activity = create_activity(client, admin_token, club_id)
    response = client.patch(
        f"/activities/{activity['id']}",
        headers=auth_header(user_token),
        json={"title": "Test"},
    )
    assert response.status_code == 403


def test_delete_activity_requires_owner(client, admin_token, user_token):
    club_id = create_club(client, admin_token)
    activity = create_activity(client, admin_token, club_id)
    response = client.delete(
        f"/activities/{activity['id']}",
        headers=auth_header(user_token),
    )
    assert response.status_code == 403


def test_get_missing_activity(client, admin_token):
    response = client.get(
        "/activities/999999999",
        headers=auth_header(admin_token),
    )
    assert response.status_code == 404


def test_wrong_club_activity_access_is_rejected(client, admin_token):
    first_club_id = create_club(client, admin_token)
    activity = create_activity(client, admin_token, first_club_id)
    second_club_id = create_club(client, admin_token)

    response = client.get(
        f"/clubs/{second_club_id}/activities/{activity['id']}",
        headers=auth_header(admin_token),
    )
    assert response.status_code in (404, 405)


def test_activity_filter_and_pagination(client, admin_token):
    club_id = create_club(client, admin_token)
    create_activity(client, admin_token, club_id, title="Python FastAPI", priority="HIGH")
    create_activity(client, admin_token, club_id, title="SQLAlchemy", priority="LOW")

    response = client.get(
        f"/clubs/{club_id}/activities",
        headers=auth_header(admin_token),
        params={
            "search": "Python",
            "priority": "HIGH",
            "limit": 1,
            "offset": 0,
            "sort_by": "title",
            "sort_order": "asc",
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["title"] == "Python FastAPI"


def test_create_activity_rejects_non_member_assignee(client, admin_token):
    club_id = create_club(client, admin_token)
    response = client.post(
        f"/clubs/{club_id}/activities",
        headers=auth_header(admin_token),
        json={"title": "Test", "assignee_id": 999999999},
    )
    assert response.status_code == 403


def test_invalid_activity_payload(client, admin_token):
    club_id = create_club(client, admin_token)
    response = client.post(
        f"/clubs/{club_id}/activities",
        headers=auth_header(admin_token),
        json={"title": "   "},
    )
    assert response.status_code == 422


def test_invalid_activity_query(client, admin_token):
    club_id = create_club(client, admin_token)
    response = client.get(
        f"/clubs/{club_id}/activities",
        headers=auth_header(admin_token),
        params={"limit": 101},
    )
    assert response.status_code == 422