import psycopg2
import pytest

from test_framework.factories.factories import UserFactory
from test_framework.helpers.user_helper import create_user_success


@pytest.fixture
def user():
    yield UserFactory.build()


@pytest.fixture
def create_user(my_live_server, user):
    yield create_user_success(my_live_server, user)


def test_register_creates_user(my_live_server, user):
    create_user_success(my_live_server, user)


def test_register_duplicate_email_is_rejected(my_live_server, client_api, create_user):
    user = UserFactory.build(email=create_user["email"])

    payload = {"user": {"email": user.email, "username": user.username, "password": user.password}}

    response = client_api.post("/users", json=payload)

    assert response.status_code == 409
    assert response.json() == {"errors": {"email": ["has already been taken"]}}
    db_connection = psycopg2.connect(my_live_server.db_url)
    with db_connection.cursor() as cur:
        cur.execute("SELECT COUNT(*) from accounts_user WHERE username= %s;", (user.username,))
        result = cur.fetchone()
        assert result[0] == 0
        cur.execute("SELECT COUNT(*) from accounts_user WHERE email= %s;", (user.email,))
        result = cur.fetchone()
        assert result[0] == 1


def test_current_user_requires_a_token(client_api):
    response = client_api.get("/user")

    assert response.status_code == 401


def test_login_token_unlocks_current_user(my_live_server, client_api, user):
    curr_user = create_user_success(my_live_server, user)
    login = client_api.post(
        "/users/login",
        json={"user": {"email": curr_user["email"], "password": curr_user["password"]}},
    )
    assert login.status_code == 200
    token = login.json()["user"]["token"]

    response = client_api.get("/user", auth_token=token)

    assert response.status_code == 200
    assert response.json()["user"]["username"] == curr_user["username"]
