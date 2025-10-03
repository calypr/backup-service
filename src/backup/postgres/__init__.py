from dataclasses import dataclass
from pathlib import Path
from psycopg2.extensions import connection
import logging
import os
import psycopg2
import shutil
import subprocess


@dataclass
class PGConfig:
    """Postgres config"""

    host: str
    port: int
    user: str


def _connect(pgConfig: PGConfig) -> connection:
    """
    Connects to a given Postgres instance.
    """
    assert pgConfig.host, "Host must not be empty"
    assert pgConfig.port, "Port must not be empty"
    assert pgConfig.user, "User must not be empty"

    try:
        connection = psycopg2.connect(
            user=pgConfig.user,
            host=pgConfig.host,
            port=pgConfig.port,
        )
    except Exception as err:
        logging.error(f"Error connecting to Postgres: {err}")
        raise

    return connection


def _getDbs(pgConfig: PGConfig) -> list[str]:
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


def _dump(pgConfig: PGConfig, db: str, dir: Path) -> Path:
    """
    Creates a single database dump.
    """
    pg_dump = shutil.which("pg_dump")

    if not pg_dump:
        raise FileNotFoundError("pg_dump not found in PATH")

    command = [
        pg_dump,
        "-U",
        pgConfig.user,
        "-h",
        pgConfig.host,
        "-p",
        str(pgConfig.port),
        "-d",
        db,
        "--format=c",
        "--no-password",
    ]

    # Dump File
    dump = Path(f"{dir}/{db}.sql")

    # We open the output file and direct the command's stdout to it.
    logging.debug(f"Dumping database '{db}' to '{dump}'")
    logging.debug(f"Command: {' '.join(command)}")
    with open(dump, "wb") as out:
        try:
            _ = subprocess.run(
                command,
                stdout=out,
                stderr=subprocess.PIPE,
                check=True,
                env=os.environ.copy(),
            )
        except subprocess.CalledProcessError as e:
            logging.error(
                f"Error dumping database '{db}': {e}, stderr: {e.stderr.decode() if e.stderr else ''}"
            )
            raise

    return dump


def _restore(pgConfig: PGConfig, db: str, dir: Path) -> Path:
    """
    Restores a single database from a dump file.
    """
    dump = dir / Path(f"{db}.sql")

    if not dump.exists():
        logging.error(f"Dump file {dump} does not exist")
        raise FileNotFoundError(f"Dump file {dump} does not exist")

    if not shutil.which("pg_restore"):
        logging.error("pg_restore not found in PATH")

    command = [
        "pg_restore",
        "-U",
        pgConfig.user,
        "-h",
        pgConfig.host,
        "-p",
        str(pgConfig.port),
        "-d",
        db,
        "--no-password",
        dump.as_posix(),
    ]

    try:
        logging.debug(f"Restoring database '{db}' from dump '{dump}'")
        logging.debug(f"Command: {' '.join(command)}")
        _ = subprocess.run(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True,
        )
        return dump

    except subprocess.CalledProcessError as e:
        raise
