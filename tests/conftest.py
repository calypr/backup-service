import pytest
from dataclasses import dataclass

from testcontainers.postgres import PostgresContainer
import psycopg2

# List of databases to be created
databases = [
    "arborist-test",
    "fence-test",
    "gecko-test",
    "indexd-test",
    "requestor-test",
]

@dataclass
class Connection:
    """A data class to hold database connection details."""
    user: str
    password: str
    host: str
    port: int
    url: str

@pytest.fixture(scope="session")
def test_database():
    """
    Pytest fixture that starts an ephemeral Postgres container for the test session.

    This fixture will:
    1. Start a Postgres Docker container.
    2. Wait until the container is ready to accept connections.
    3. Run the database initialization script to create the required databases.
    4. Yield the connection URL to the tests.
    5. Automatically stop and remove the container after the test session ends.
    """
    # Define the postgres container, can specify image version
    postgres_container = PostgresContainer("postgres")

    with postgres_container as postgres:
        print("Postgres container started. Initializing databases...")

        host = "localhost"
        user = postgres.username # default: test
        password = postgres.password # default: test
        port = postgres.port # randomly assigned port

        initialize(host=host, user=user, password=password)

        # Provide the connection URL to the tests
        url = postgres.get_connection_url()

        connection_info = Connection(
            user=user,
            password=password,
            host=host,
            port=int(port),
            url=postgres.get_connection_url()
        )

        print(f"Databases are ready. Connection URL: {url}")
        yield connection_info

        print("Test session finished. Tearing down Postgres container.")


def initialize(host: str, user: str, password: str):
    """
    Initializes the database by creating the required databases.

    This function connects to the Postgres instance and runs SQL commands to set up the necessary databases.
    """

    try:
        # Connect to the default 'postgres' database to run initialization commands
        conn = psycopg2.connect(
            dbname="postgres",
            user=user,
            password=password,
            host=host,
            port=5432,
        )
        conn.autocommit = True  # Enable autocommit mode for database creation

        with conn.cursor() as cursor:
            # Create a new database for testing
            for db_name in databases:
                cursor.execute(f"CREATE DATABASE {db_name};")
                print(f"Database '{db_name}' created successfully.")

    except psycopg2.Error as e:
        print(f"Error during database initialization: {e}")
