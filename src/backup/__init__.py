import psycopg2
from psycopg2.extensions import connection
from typing import Optional
from pathlib import Path


def connect(host: str, user: str, password: str) -> Optional[connection]:
    """
    Connects to a given database.
    """
    assert host, "Host must not be empty"
    assert user, "User must not be empty"
    assert password, "Password must not be empty"

    try:
        connection = psycopg2.connect(
            user=user,
            password=password,
            host=host,
            port=5432,
        )
    except psycopg2.Error as e:
        print(f"Error connecting to the database: {e}")
        return None

    return connection


def dump(url: str) -> Optional[str]:
    """
    Creates a database dump.
    """
    assert url is not None, "Database URL must not be None"



def upload(dump_file: str, bucket: str):
    """
    Uploads a file to S3.
    """
    assert dump_file, "Dump file path must not be empty"
    assert bucket, "Bucket name must not be empty"

    dump_path = Path(dump_file)
    if not dump_path.exists():
        print(f"Dump file {dump_file} does not exist.")
        return

    pass
