import os

import psycopg2


class MyPostgreSQL:

    db_connection = None

    def __init__(self):
        self.db_connection = psycopg2.connect(os.environ("DATABASE_URL"))


