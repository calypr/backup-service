from backup.elasticsearch import (
    ElasticSearchConfig,
    _getIndices,
    _dump as _esDump,
    _restore as _esRestore,
)
from backup.grip import (
    GripConfig,
    _getEdges,
    _getVertices,
    _dump as _gripDump,
    _restore as _gripRestore,
)
from backup.postgres import (
    PostgresConfig,
    _getDbs,
    _dump as _pgDump,
    _restore as _pgRestore,
)
from backup.s3 import (
    S3Config,
    _download,
    _upload,
)
from backup.utils import postgres_options, s3_options, dir_options
import click
from click_aliases import ClickAliasedGroup
from datetime import datetime
import logging
from pathlib import Path


@click.group(cls=ClickAliasedGroup)
@click.version_option()
@click.option(
    "--verbose",
    "-v",
    "--debug",
    is_flag=True,
    default=False,
    help="Enable verbose (DEBUG) logging.",
)
def cli(verbose: bool):
    # Default logging level is INFO
    level = logging.INFO

    # If the flag is provided set logging level to DEBUG
    if verbose:
        level = logging.DEBUG

    logging.basicConfig(
        level=level,
        format="%(asctime)s - %(levelname)s - %(message)s",
    )


if __name__ == "__main__":
    cli()


@cli.group(aliases=['pg'])
def postgres():
    """Commands for Postgres backups."""
    pass


@postgres.command()
@postgres_options
@s3_options
def backup(
    host: str,
    port: int,
    user: str,
    password: str,
    endpoint: str,
    dir: Path,
    bucket: str,
    key: str,
    secret: str,
):
    """Postgres ➜ S3"""
    p = PostgresConfig(host=host, port=port, user=user, password=password)
    s3 = S3Config(endpoint=endpoint, bucket=bucket, key=key, secret=secret)

    # List databases
    dbs = _getDbs(p)

    if not dbs:
        logging.warning("No databases found to backup.")
        return

    # Dump databases
    for database in dbs:
        _ = _pgDump(p, database, dir)

    # Upload dumps to S3
    _ = _upload(s3, dir)


@postgres.command()
@postgres_options
@dir_options
def restore(host: str, port: int, user: str, password: str, dir: Path):
    """Local ➜ Postgres"""
    p = PostgresConfig(host=host, port=port, user=user, password=password)

    dbs = _getDbs(p)
    if not dbs:
        logging.warning("No databases found to restore.")
        return

    # Restore databases
    for database in dbs:
        _ = _pgRestore(p, database, dir)


@postgres.command(name="ls")
@postgres_options
def listDbs(host: str, port: int, user: str, password: str):
    """List databases"""
    p = PostgresConfig(host=host, port=port, user=user, password=password)

    dbs = _getDbs(p)
    if not dbs:
        logging.warning("No databases found.")
        return

    # List databases
    for database in dbs:
        click.echo(database)


@postgres.command()
@postgres_options
@dir_options
def dump(host: str, port: int, user: str, password: str, dir: Path):
    """Postgres ➜ local"""
    p = PostgresConfig(host=host, port=port, user=user, password=password)

    # Shared timestamp for all dumps
    timestamp = datetime.now().isoformat()

    # Dump directory
    out = dir / Path(timestamp)
    out.mkdir(parents=True, exist_ok=True)

    dbs = _getDbs(p)
    if not dbs:
        logging.warning("No databases found to dump.")
        return

    # Dump databases
    for database in dbs:
        dump = _pgDump(p, database, out)
        logging.debug(f"Dumped {database} to {dump}")


@postgres.command()
@s3_options
@dir_options
def download(endpoint: str, bucket: str, key: str, secret: str, dir: Path):
    """S3 ➜ local"""
    s3 = S3Config(endpoint=endpoint, bucket=bucket, key=key, secret=secret)

    # Download from S3
    _ = _download(s3, dir)


@postgres.command()
@s3_options
@dir_options
def upload(endpoint: str, bucket: str, key: str, secret: str, dir: Path):
    """local ➜ S3"""
    s3 = S3Config(endpoint=endpoint, bucket=bucket, key=key, secret=secret)

    # Upload to S3
    _ = _upload(s3, dir)


@cli.group(aliases=['es'])
def elasticsearch():
    """Commands for ElasticSearch backups."""
    pass
