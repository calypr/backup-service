from pathlib import Path
import click
from backup import (
    PostgresConfig,
    S3Config,
    _download,
    _dump,
    _getDbs,
    _restore,
    _upload,
)
from .utils import postgres_options, s3_options, dir_options
import logging


@click.group()
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


@cli.command()
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

    # Dump databases
    for database in dbs:
        _ = _dump(p, database, dir)

    # Upload dumps to S3
    _ = _upload(s3, dir)


@cli.command()
@postgres_options
@dir_options
def restore(host: str, port: int, user: str, password: str, dir: Path):
    """S3 ➜ Postgres"""
    p = PostgresConfig(host=host, port=port, user=user, password=password)

    # Restore databases
    for database in _getDbs(p):
        _ = _restore(p, database, dir)


@cli.command(name="ls")
@postgres_options
def listDbs(host: str, port: int, user: str, password: str):
    """List databases"""
    p = PostgresConfig(host=host, port=port, user=user, password=password)

    # List databases
    for database in _getDbs(p):
        click.echo(database)


@cli.command()
@postgres_options
@dir_options
def dump(host: str, port: int, user: str, password: str, dir: Path):
    """Postgres ➜ local"""
    p = PostgresConfig(host=host, port=port, user=user, password=password)

    # Dump databases
    for database in _getDbs(p):
        dump = _dump(p, database, dir)
        logging.debug(f"Dumped {database} to {dump}")


@cli.command()
@s3_options
@dir_options
def download(endpoint: str, bucket: str, key: str, secret: str, dir: Path):
    """S3 ➜ local"""
    s3 = S3Config(endpoint=endpoint, bucket=bucket, key=key, secret=secret)

    # Download from S3
    _ = _download(s3, dir)


@cli.command()
@s3_options
@dir_options
def upload(endpoint: str, bucket: str, key: str, secret: str, dir: Path):
    """local ➜ S3"""
    s3 = S3Config(endpoint=endpoint, bucket=bucket, key=key, secret=secret)

    # Upload to S3
    _ = _upload(s3, dir)


if __name__ == "__main__":
    cli()
