import psycopg2

def create_user_success(my_live_server, myapi, test_user):
    payload = {"user": {"email": test_user.email, "username": test_user.username, "password": test_user.password}}
    response = myapi.post("/users", json=payload)
    assert response.status_code == 201
    body = response.json()["user"]
    assert body["email"] == test_user.email
    assert body["username"] == test_user.username
    assert body["token"]
    db_connection = psycopg2.connect(my_live_server["DATABASE_URL"])
    with db_connection.cursor() as cur:
        cur.execute("SELECT COUNT(*) FROM accounts_user WHERE email = %s;", (test_user.email,))
        result = cur.fetchone()
        assert result[0]==1
    db_connection.close()
    body["password"] = test_user.password
    return body