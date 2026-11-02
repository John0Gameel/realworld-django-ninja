import pytest
from django.contrib.auth import get_user_model

User = get_user_model()

# Every test in this module may touch the database (same as decorating each one with @pytest.mark.django_db)

PASSWORD = "correct-horse-battery"


@pytest.fixture
def user():
    return User.objects.create_user(email="me@example.com", username="me", password=PASSWORD)


def test_register_creates_user(client):
    payload = {"user": {"email": "new@example.com", "username": "newbie", "password": PASSWORD}}

    response = client.post("/api/users", data=payload, content_type="application/json")

    assert response.status_code == 201
    body = response.json()["user"]
    assert body["email"] == "new@example.com"
    assert body["username"] == "newbie"
    assert body["token"]
    # the request went through the whole stack and really wrote a row
    assert User.objects.filter(username="newbie").exists()


def test_register_duplicate_email_is_rejected(client, user):
    payload = {"user": {"email": user.email, "username": "someone-else", "password": PASSWORD}}

    response = client.post("/api/users", data=payload, content_type="application/json")

    assert response.status_code == 409
    print(response.json())
    print(response)
    assert response.json() == {"errors": {"email": ["has already been taken"]}}
    assert User.objects.filter(username="someone-else").count() == 0
    assert User.objects.filter(email=user.email).count() == 1
    # No DB query after this point: the IntegrityError poisoned the transaction wrapping this test.
    # To query afterwards, use @pytest.mark.django_db(transaction=True) (slower, but really commits).


def test_current_user_requires_a_token(client):
    response = client.get("/api/user")

    assert response.status_code == 401


def test_login_token_unlocks_current_user(client, user):
    login = client.post(
        "/api/users/login",
        data={"user": {"email": user.email, "password": PASSWORD}},
        content_type="application/json",
    )
    assert login.status_code == 200
    token = login.json()["user"]["token"]

    response = client.get("/api/user", headers={"Authorization": f"Token {token}"})

    assert response.status_code == 200
    assert response.json()["user"]["username"] == "me"
