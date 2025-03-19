import psycopg2
import psycopg2.pool
from contextlib import contextmanager

from . import config

# Get from config/app.config
host = config.get_str("database", "host")
port = config.get_str("database", "port")
dbname = config.get_str("database", "db")
user = config.get_str("database", "user")
password = config.get_str("database", "password")

# Database connection string
DATABASE_URL = f"postgresql://{user}:{password}@{host}:{port}/{dbname}"
SCHEMA_NAME = config.get_str("database", "schema")

# Initialize the connection pool
try:
    connection_pool = psycopg2.pool.SimpleConnectionPool(
        1,  # Minimum number of connections
        10, # Maximum number of connections
        DATABASE_URL
    )
except Exception as e:
    print(e)
    connection_pool = None

@contextmanager
def get_db():
    if connection_pool is None:
        yield None
        return
    conn = connection_pool.getconn()
    try:
        yield conn
    finally:
        connection_pool.putconn(conn)
