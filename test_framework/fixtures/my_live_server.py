import os
import subprocess
import time

import psycopg2
import pytest

from test_framework.helpers.my_api import MyAPI

TEMP_DB_NAME = "qa_test"
SERVER_PORT = 8001


class MyLiveServer:
    db_url = ""
    base_url = ""
    base_api_url = ""
    myapi = None

    def __init__(self, db_url, base_url):
        self.db_url = db_url
        self.base_url = base_url
        self.base_api_url = base_url + "/api"
        self.myapi = MyAPI(self.base_api_url, auth_type="Token")


@pytest.fixture(scope="session")
def my_live_db():
    db_connection = psycopg2.connect(os.getenv("DATABASE_URL"))
    db_connection.autocommit = True
    with db_connection.cursor() as cur:
        cur.execute(f"CREATE DATABASE {TEMP_DB_NAME};")
    yield TEMP_DB_NAME
    with db_connection.cursor() as cur:
        cur.execute("DROP DATABASE qa_test WITH (FORCE);")
    db_connection.close()


@pytest.fixture(autouse=True, scope="session")
def my_live_server(my_live_db):
    databaseurl = f"postgresql://postgres:0000@localhost:5433/{my_live_db}"
    subprocess.run(
        [
            "make",
            "migrate",
        ],
        env={**os.environ, "DATABASE_URL": databaseurl},
        capture_output=True,
        text=True,
        check=True,
    )
    app_process = subprocess.Popen(
        ["uv", "run", "python", "manage.py", "runserver", f"0.0.0.0:{SERVER_PORT}", "--noreload"],
        env={**os.environ, "DATABASE_URL": databaseurl, "ALLOWED_HOSTS": "*"},
    )
    time.sleep(5)
    yield MyLiveServer(db_url=databaseurl, base_url=f"http://localhost:{SERVER_PORT}")
    app_process.terminate()


@pytest.fixture(autouse=True, scope="session")
def client_api(my_live_server):
    yield my_live_server.myapi
