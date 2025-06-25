from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from psycopg2.extensions import connection
from typing import Optional
import boto3
import psycopg2
import subprocess


@dataclass
class PostgresConfig:
    """Postgres database connection detail"""

    host: str
    port: int
    user: str
    password: str


@dataclass
class S3Config:
    """S3 configuration details"""

    endpoint_url: str
    bucket: str
    key: str
    secret: str


def connect(p: PostgresConfig) -> connection:
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
        print(f"Error connecting to the database: {e}")
        raise

    return connection


def listDbs(c: connection) -> list[str]:
    """
    Retrieves the names of all databases in the PostgreSQL server.
    """
    assert c is not None, "Database connection must not be None"

    with c.cursor() as cur:
        cur.execute("SELECT datname FROM pg_database WHERE datistemplate = false;")
        db_names = [row[0] for row in cur.fetchall()]

    return db_names


def dumpDbs(p: PostgresConfig, dbs: list[str]) -> Path:
    """
    Dumps all databases to a specified directory.
    """

    # Shared timestamp for all dumps
    timestamp = datetime.now().isoformat()

    # Dump directory
    dir = Path("backups") / timestamp
    dir.mkdir(parents=True, exist_ok=True)

    for db in dbs:
        dumpFile = _dumpDb(p, db, dir)
        if not dumpFile:
            print("Failed to create database dump.")
            raise

    for database in dbs:
        _dumpDb(p, database, dir)

    return dir


def _dumpDb(p: PostgresConfig, database: str, dir: Path) -> Optional[Path]:
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

    # Dump File
    dump = Path(f"{dir}/{database}.sql")

    try:
        # We open the output file and direct the command's stdout to it.
        with open(dump, "wb") as out:
            _ = subprocess.run(
                command,
                stdout=out,
                stderr=subprocess.PIPE,
                check=True,
            )
        print(f"Successfully created backup: {dump}")
        return dump

    except subprocess.CalledProcessError as e:
        print(f"Error dumping database '{database}': {e.stderr}")
        return None


def upload(
    s3: S3Config,
    dir: Path,
):
    """
    Uploads a file to S3 (MinIO/Ceph compatible).
    """
    try:
        client = boto3.client(
            "s3",
            endpoint_url=s3.endpoint_url,
            aws_access_key_id=s3.key,
            aws_secret_access_key=s3.secret,
        )
        for dump in dir.glob("*.sql"):
            print(f"Uploading {dump} to bucket {s3.bucket} as {dump.name}")
            client.upload_file(dump, s3.bucket, dump.name)

    except Exception as err:
        print(f"Failed to upload files to S3: {err}")
