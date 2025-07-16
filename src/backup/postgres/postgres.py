from dataclasses import dataclass
import logging
from pathlib import Path
from psycopg2.extensions import connection
import psycopg2
import subprocess


@dataclass
class PostgresConfig:
    """Postgres config"""

    host: str
    port: int
    user: str
    password: str


def _connect(pgConfig: PostgresConfig) -> connection:
    """
    Connects to a given Postgres instance.
    """
    assert pgConfig.host, "Host must not be empty"
    assert pgConfig.port, "Port must not be empty"
    assert pgConfig.user, "User must not be empty"
    assert pgConfig.password, "Password must not be empty"

    try:
        connection = psycopg2.connect(
            user=pgConfig.user,
            password=pgConfig.password,
            host=pgConfig.host,
            port=pgConfig.port,
        )
    except Exception as err:
        logging.error(f"Error connecting to Postgres: {err}")
        raise

    return connection


def _getDbs(pgConfig: PostgresConfig) -> list[str] | None:
    """
    Utiltity function to connect to Postgres and list all databases.
    """

    # Connect to Postgres
    c = _connect(pgConfig)

    # List databases
    dbs = []
    with c.cursor() as cur:
        cur.execute("SELECT datname FROM pg_database WHERE datistemplate = false;")
        dbs = [row[0] for row in cur.fetchall()]

    return dbs


def _dump(postgres: PostgresConfig, database: str, dir: Path) -> Path | None:
    """
    Creates a single database dump.
    """
    command = [
        "pg_dump",
        "-U",
        postgres.user,
        "-h",
        postgres.host,
        "-p",
        str(postgres.port),
        "-d",
        database,
        "--format=c",
        "--no-password",
    ]

    # Dump File
    dump = Path(f"{dir}/{database}.sql")

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
        return None


def _restore(pgConfig: PostgresConfig, database: str, dir: Path) -> Path | None:
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
        pgConfig.user,
        "-h",
        pgConfig.host,
        "-p",
        str(pgConfig.port),
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

