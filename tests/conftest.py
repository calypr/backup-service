import logging
from pathlib import Path
from testcontainers.postgres import PostgresContainer
from testcontainers.minio import MinioContainer
from minio import Minio
import pytest
from backup import PostgresConfig, S3Config


@pytest.fixture(scope="session")
def testPostgres():
    """
    Eephemeral Postgres container for the test session
    """

    # List of ephemeral databases to be created in the Postgres container
    databases = [
        "arborist-test",
        "fence-test",
        "gecko-test",
        "indexd-test",
        "requestor-test",
    ]

    with PostgresContainer("postgres") as p:
        logging.debug(f"Postgres ready at {p.get_connection_url}")

        yield PostgresConfig(
            user=p.username,
            password=p.password,
            host="localhost",
            port=p.get_exposed_port(5432),
        )


@pytest.fixture(scope="session")
def testS3():
    """
    Ephemeral S3 configuration for the test session
    """

    with MinioContainer() as m:

        # Get connection parameters
        host = m.get_container_host_ip()
        port = m.get_exposed_port(m.port)

        key = m.access_key
        secret = m.secret_key
        endpoint = f"{host}:{port}"
        logging.debug(f"MinIO ready at {endpoint}")

        # MinIO client
        client = Minio(
            f"{host}:{port}", access_key=key, secret_key=secret, secure=False
        )

        # Test bucket
        bucket = "test"
        client.make_bucket(bucket)
        logging.debug(f"Created bucket: {bucket}")

        yield S3Config(endpoint=f"{host}:{port}", bucket=bucket, key=key, secret=secret)


@pytest.fixture(scope="session")
def testDir():
    """
    Temporary directory for the test session
    """

    return Path("tests/fixtures")
