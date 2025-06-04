import psycopg2
import psycopg2.pool
from contextlib import contextmanager
from time import sleep
from fastapi import HTTPException

from . import config

# Get from config/app.config
host = config.get_str("database", "host")
port = config.get_str("database", "port")
dbname = config.get_str("database", "db")
user = config.get_str("database", "user")
password = config.get_str("database", "password")

# Database connection string
DATABASE_URL = f"postgresql://{user}:{password}@{host}:{port}/{dbname}"
DEFAULT_SCHEMA = config.get_str("database", "schema")

connection_pool = None


def init_conn_pool():
    global connection_pool
    # Initialize the connection pool
    try:
        connection_pool = psycopg2.pool.SimpleConnectionPool(
            1,   # Minimum number of connections
            10,  # Maximum number of connections
            DATABASE_URL
        )
    except Exception as e:
        print(e)
        connection_pool = None


init_conn_pool()


@contextmanager
def get_db():
    global connection_pool
    max_tries = 2
    n_try = 0
    while connection_pool is None and n_try < max_tries:
        init_conn_pool()
        n_try += 1
        if connection_pool is None:
            sleep(5)

    if connection_pool is None:
        yield None
        return
    conn = connection_pool.getconn()
    try:
        yield conn
    finally:
        connection_pool.putconn(conn)


def validate_schema(schema: str) -> bool:
    """Validate if a schema exists in the database"""
    with get_db() as conn:
        if conn is None:
            raise HTTPException(status_code=500, detail="Database connection failed")
        try:
            with conn.cursor() as cursor:
                cursor.execute("SELECT schema_name FROM information_schema.schemata WHERE schema_name = %s", (schema,))
                return cursor.fetchone() is not None
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
