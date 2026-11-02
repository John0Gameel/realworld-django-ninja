import pytest
import psycopg2
from test_framework.factories.user_factory import UserFactory
from test_framework.helpers.my_api import MyAPI
from test_framework.helpers.user_helper import create_user_success
    

@pytest.fixture
def user():
    yield UserFactory()

@pytest.fixture
def myapi(my_live_server):
    yield MyAPI(base_url=my_live_server["BASE_URL"], auth_type="Token")

@pytest.fixture
def create_user(my_live_server, myapi, user):
    yield create_user_success(my_live_server, myapi, user)


def test_register_creates_user(my_live_server, myapi, user):
    create_user_success(my_live_server, myapi, user)

def test_register_duplicate_email_is_rejected(my_live_server, myapi, create_user):
    user = UserFactory(email=create_user["email"])
    
    payload = {"user": {"email": user.email, "username": user.username, "password": user.password}}

    response = myapi.post("/users", json=payload)

    assert response.status_code == 409
    print(response.json())
    print(response)
    assert response.json() == {"errors": {"email": ["has already been taken"]}}
    db_connection = psycopg2.connect(my_live_server["DATABASE_URL"])
    with db_connection.cursor() as cur:
        cur.execute("SELECT COUNT(*) from accounts_user WHERE username= %s;", (user.username,))
        result = cur.fetchone()
        assert result[0] == 0
        cur.execute("SELECT COUNT(*) from accounts_user WHERE email= %s;", (user.email,))
        result = cur.fetchone()
        assert result[0] == 1
    
def test_current_user_requires_a_token(myapi):
    response = myapi.get("/user")

    assert response.status_code == 401

def test_login_token_unlocks_current_user(my_live_server, myapi, user):
    curr_user = create_user_success(my_live_server, myapi, user)
    login = myapi.post(
        "/users/login",
        json={"user": {"email": curr_user["email"], "password": curr_user["password"]}},
    )
    assert login.status_code == 200
    token = login.json()["user"]["token"]

    response = myapi.get("/user", auth_token=token)

    assert response.status_code == 200
    assert response.json()["user"]["username"] == curr_user["username"]
