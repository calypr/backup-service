import click
from backup import (
    PostgresConfig,
    S3Config,
    _connect,
    _download,
    _dump,
    _getDbs,
    _listDbs,
    _restore,
    _upload,
)
from .utils import postgres_options, s3_options, dir_options
import logging


@click.group(context_settings=dict(allow_interspersed_args=True))
@click.version_option()
@click.option(
    "--verbose",
    "-v",
    "--debug",
    is_flag=True,
    default=False,
    help="Enable verbose (DEBUG) logging.",
)
def cli(verbose):
    # Set the default level to INFO
    level = logging.INFO

    # If the flag is set, change the level to DEBUG
    if verbose:
        level = logging.DEBUG
    
    # Configure logging once with the determined level
    logging.basicConfig(
        level=level,
        format="%(asctime)s - %(levelname)s - %(message)s",
    )

@cli.command()
@postgres_options
@s3_options
def backup(host, port, user, password, endpoint, dir, bucket, key, secret):
    """Postgres ➜ S3"""
    p = PostgresConfig(host=host, port=port, user=user, password=password)
    s3 = S3Config(endpoint_url=endpoint, bucket=bucket, key=key, secret=secret)

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
def restore(host, port, user, password, dir):
    """S3 ➜ Postgres"""
    p = PostgresConfig(host=host, port=port, user=user, password=password)

    # Restore databases
    for database in _getDbs(p):
        _ = _restore(p, database, dir)



@cli.command(name="ls")
@postgres_options
def listDbs(host, port, user, password):
    """List databases"""
    p = PostgresConfig(host=host, port=port, user=user, password=password)

    # List databases
    for database in _getDbs(p):
        print(database)



@cli.command()
@postgres_options
@dir_options
def dump(host, port, user, password, dir):
    """Postgres ➜ local"""
    p = PostgresConfig(host=host, port=port, user=user, password=password)

    # Dump databases
    for database in _getDbs(p):
        dump = _dump(p, database, dir)
        print(f"Dumped {database} to {dump}")


@cli.command()
@s3_options
@dir_options
def download(endpoint, bucket, key, secret, dir):
    """S3 ➜ local"""
    s3 = S3Config(endpoint_url=endpoint, bucket=bucket, key=key, secret=secret)

    # Download from S3
    err = _download(s3, dir)
    if err:
        print(f"Error uploading to S3: {err}")
    else:
        print("Upload OK")


@cli.command()
@s3_options
@dir_options
def upload(endpoint, bucket, key, secret, dir):
    """local ➜ S3"""
    s3 = S3Config(endpoint_url=endpoint, bucket=bucket, key=key, secret=secret)

    # Upload to S3
    err = _upload(s3, dir)
    if err:
        print(f"Error uploading to S3: {err}")
    else:
        print("Upload OK")


if __name__ == "__main__":
    cli()
