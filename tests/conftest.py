from testcontainers.postgres import PostgresContainer
import pytest
from backup import PostgresConfig

# List of ephemeral databases to be created in the Postgres container
databases = [
    "arborist-test",
    "fence-test",
    "gecko-test",
    "indexd-test",
    "requestor-test",
]


@pytest.fixture(scope="session")
def testPostgres():
    """
    Eephemeral Postgres container for the test session
    """
    with PostgresContainer("postgres") as p:
        print("Postgres container started. Initializing databases...")

        connection_info = PostgresConfig(
            user=p.username,
            password=p.password,
            host="localhost",
            port=p.get_exposed_port(5432),
        )

        print(f"Databases are ready. Connection URL: {p.get_connection_url}")

        yield connection_info

        print("Test session finished. Tearing down Postgres container...")
