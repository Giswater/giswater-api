import psycopg2
import psycopg2.pool
import configparser
from contextlib import contextmanager

# Get from config/app.config
config_file = "app/config/app.config"
cp = configparser.ConfigParser()
cp.read(config_file)
host = cp.get("database", "host")
port = cp.get("database", "port")
dbname = cp.get("database", "db")
user = cp.get("database", "user")
password = cp.get("database", "password")

# Database connection string
DATABASE_URL = f"postgresql://{user}:{password}@{host}:{port}/{dbname}"
SCHEMA_NAME = cp.get("database", "schema")

# Initialize the connection pool
connection_pool = psycopg2.pool.SimpleConnectionPool(
    1,  # Minimum number of connections
    10, # Maximum number of connections
    DATABASE_URL
)

@contextmanager
def get_db():
    conn = connection_pool.getconn()
    try:
        yield conn
    finally:
        connection_pool.putconn(conn)
