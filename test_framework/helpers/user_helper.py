import psycopg2

from test_framework.factories.factories import UsersPostRequestFactory


def create_user_success(my_live_server, test_user):
    payload = UsersPostRequestFactory.build(user=test_user)
    response = my_live_server.myapi.post("/users", json=payload)
    assert response.status_code == 201
    body = response.json()["user"]
    assert body["email"] == test_user.email
    assert body["username"] == test_user.username
    assert body["token"]
    db_connection = psycopg2.connect(my_live_server.db_url)
    with db_connection.cursor() as cur:
        cur.execute("SELECT COUNT(*) FROM accounts_user WHERE email = %s;", (test_user.email,))
        result = cur.fetchone()
        assert result[0] == 1
    db_connection.close()
    body["password"] = test_user.password
    return body
