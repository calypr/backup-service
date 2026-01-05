import os
from backup.postgres import PGConfig
from backup.s3 import S3Config
from minio import Minio
from minio.credentials.providers import EnvAWSProvider
from pathlib import Path
from testcontainers.minio import MinioContainer
from testcontainers.postgres import PostgresContainer
import logging
import pytest


@pytest.fixture(scope="session")
def testPostgres():
    """
    Eephemeral Postgres container for the test session
    """

    # List of ephemeral databases to be created in the Postgres container
    dbs = [
        "arborist-test",
        "fence-test",
        "gecko-test",
        "indexd-test",
        "requestor-test",
    ]

    with PostgresContainer("postgres") as postgres:
        logging.debug(f"Postgres ready at {postgres.get_connection_url}")

        # Set PGPASSWORD environment variable for authentication
        os.environ["PGPASSWORD"] = postgres.password

        yield PGConfig(
            # Default: test
            user=postgres.username,
            host="localhost",
            port=postgres.get_exposed_port(5432),
        )


@pytest.fixture(scope="session")
def testS3():
    """
    Ephemeral S3 configuration for the test session
    """

    with MinioContainer() as minio:

        # Get connection parameters
        host = minio.get_container_host_ip()
        port = minio.get_exposed_port(minio.port)

        os.environ["AWS_ACCESS_KEY_ID"] = minio.access_key
        os.environ["AWS_SECRET_ACCESS_KEY"] = minio.secret_key

        endpoint = f"{host}:{port}"
        logging.debug(f"MinIO ready at {endpoint}")

        # MinIO client
        client = Minio(f"{host}:{port}", credentials=EnvAWSProvider(), secure=False)

        # Test bucket
        bucket = "test"
        client.make_bucket(bucket)
        logging.debug(f"Created bucket: {bucket}")

        yield S3Config(endpoint=f"{host}:{port}", bucket=bucket)


@pytest.fixture(scope="session")
def testDir():
    """
    Temporary directory for the test session
    """

    return Path("tests/fixtures")
