from dataclasses import dataclass
from datetime import datetime
import logging
from pathlib import Path
from minio import Minio
from psycopg2.extensions import connection
import boto3
from boto3.session import Config
import psycopg2
import subprocess


@dataclass
class PostgresConfig:
    """Postgres config"""

    host: str
    port: int
    user: str
    password: str


@dataclass
class S3Config:
    """S3 config"""

    endpoint: str
    bucket: str
    key: str
    secret: str


def _connect(p: PostgresConfig) -> connection:
    """
    Connects to a given database.
    """
    assert p.host, "Host must not be empty"
    assert p.port, "Port must not be empty"
    assert p.user, "User must not be empty"
    assert p.password, "Password must not be empty"

    try:
        connection = psycopg2.connect(
            user=p.user,
            password=p.password,
            host=p.host,
            port=p.port,
        )
    except Exception as e:
        logging.error(f"Error connecting to the database: {e}")
        raise

    return connection


def _getDbs(p: PostgresConfig) -> list[str]:
    """
    Utiltity function to connect to Postgres and list all databases.
    """

    # Connect to Postgres
    c = _connect(p)

    # List databases
    dbs = _listDbs(c)

    return dbs


def _listDbs(c: connection) -> list[str]:
    """
    Retrieves the names of all databases in the PostgreSQL server.
    """
    assert c is not None, "Database connection must not be None"

    with c.cursor() as cur:
        cur.execute("SELECT datname FROM pg_database WHERE datistemplate = false;")
        db_names = [row[0] for row in cur.fetchall()]

    return db_names


def _dump(p: PostgresConfig, database: str, dir: Path) -> Path:
    """
    Creates a single database dump.
    """
    command = [
        "pg_dump",
        "-U",
        p.user,
        "-h",
        p.host,
        "-p",
        str(p.port),
        "-d",
        database,
        "--format=c",
        "--no-password",
    ]

    # Shared timestamp for all dumps
    timestamp = datetime.now().isoformat()

    # Dump directory
    out = dir / Path(timestamp)
    out.mkdir(parents=True, exist_ok=True)

    # Dump File
    dump = Path(f"{out}/{database}.sql")

    try:
        # We open the output file and direct the command's stdout to it.
        logging.debug(f"Dumping database '{database}' to '{dump}'")
        logging.debug(f"Command: {' '.join(command)}")
        with open(dump, "wb") as out:
            _ = subprocess.run(
                command,
                stdout=out,
                stderr=subprocess.PIPE,
                check=True,
            )
        return dump

    except subprocess.CalledProcessError as e:
        logging.error(f"Error dumping database '{database}': {e.stderr}")
        return Path()


def _restore(p: PostgresConfig, database: str, dir: Path) -> Path | None:
    """
    Restores a single database from a dump file.
    """
    dump = dir / Path(f"{database}.sql")

    if not dump.exists():
        logging.error(f"Dump file {dump} does not exist")
        return None

    command = [
        "pg_restore",
        "-U",
        p.user,
        "-h",
        p.host,
        "-p",
        str(p.port),
        "-d",
        database,
        "--no-password",
        dump.as_posix(),
    ]

    try:
        logging.debug(f"Restoring database '{database}' from dump '{dump}'")
        logging.debug(f"Command: {' '.join(command)}")
        _ = subprocess.run(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True,
        )
        return dump

    except subprocess.CalledProcessError as e:
        logging.error(f"Error restoring database '{database}': {e.stderr}")
        return None


def _getS3Client(s3: S3Config):
    """
    Returns a MinIO client configured with the provided S3 configuration.
    """
    return Minio(
        f"{s3.endpoint}",
        access_key=s3.key,
        secret_key=s3.secret,
    )


def _upload(
    s3: S3Config,
    dir: Path,
) -> Exception | None:
    """
    Uploads a file to S3 (MinIO/Ceph compatible).
    """

    client = _getS3Client(s3)

    try:
        logging.debug(f"dir: {dir}, type: {type(dir)}")

        # TODO: Review if this selection/filter of files is acceptable
        for dump in dir.glob("*.sql"):
            logging.debug(f"Uploading {dump} to bucket {s3.bucket} as {dump.as_posix}")

            client.fput_object(
                bucket_name=s3.bucket,
                object_name=dump.as_posix(),
                file_path=dump.as_posix(),
            )

    except Exception as err:
        logging.error(f"Failed to upload files to S3: {err}")
        return err

    return None


def _download(
    s3: S3Config,
    dir: Path,
) -> Exception | None:
    """
    Downloads a file from S3 (MinIO/Ceph compatible).
    """

    client = _getS3Client(s3)

    try:
        for obj in client.list_objects(s3.bucket, recursive=True):
            name = obj.object_name
            logging.debug(f"obj: {obj}")

            if name is None:
                continue

            path = (dir / name).as_posix()

            logging.debug(f"Downloading {name} from bucket {s3.bucket} to {path}")
            _ = client.fget_object(
                bucket_name=s3.bucket,
                object_name=name,
                file_path=path,
            )

    except Exception as err:
        logging.error(f"Failed to download files from S3: {err}")
        return err

    return None
