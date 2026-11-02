import psycopg2, pytest
import os, subprocess
import time 

TEMP_DB_NAME = "qa_test"

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
            "make", "migrate", 
        ],
        env={**os.environ, "DATABASE_URL": databaseurl},
        capture_output=True, text=True, check=True
    )
    app_process = subprocess.Popen(
        [
            "uv", "run", "python", "manage.py", "runserver", "0.0.0.0:8001", "--noreload"
        ],
        env={**os.environ, "DATABASE_URL": databaseurl, "ALLOWED_HOSTS":"*"},
    )
    time.sleep(5)
    yield {"DATABASE_URL": databaseurl, "BASE_URL": f"http://localhost:8001/api"}
    app_process.terminate()
    