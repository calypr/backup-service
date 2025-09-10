from backup.grip import (
    GripConfig,
    _getEdges,
    _getVertices,
    _dump as _gripDump,
    _restore as _gripRestore,
)
from backup.postgres import (
    PGConfig,
    _getDbs,
    _dump as _pgDump,
    _restore as _pgRestore,
)
from backup.s3 import (
    S3Config,
    _download,
    _upload,
)
from backup.options import (
    dir_options,
    grip_options,
    pg_options,
    s3_options,
)
from click_aliases import ClickAliasedGroup
from datetime import datetime
from elasticsearch.exceptions import ElasticsearchWarning
from pathlib import Path
import click
import logging
import warnings
import json


@click.group(cls=ClickAliasedGroup)
@click.version_option()
@click.option(
    "--verbose",
    "-v",
    "--debug",
    is_flag=True,
    default=False,
    help="Enable debug logging.",
)
def cli(verbose: bool):
    # Set default logging level
    level = logging.WARNING

    # Set verbose logging level
    if verbose:
        level = logging.DEBUG

    logging.basicConfig(
        level=level,
        format="%(asctime)s - %(levelname)s - %(message)s",
    )

    # Avoid INFO and ElasticsearchWarning logging from the elasticsearch logger
    # https://stackoverflow.com/a/47157553
    logging.getLogger("elastic_transport.transport").setLevel(logging.CRITICAL)
    warnings.simplefilter("ignore", ElasticsearchWarning)


if __name__ == "__main__":
    cli()


@cli.group(aliases=["gp"])
def grip():
    """Commands for GRIP backups."""
    pass


@grip.command(name="ls")
@grip_options
def list_grip(host: str, port: int, graph: str, limit: int, vertex: bool, edge: bool):
    """list GRIP vertices and/or edges"""
    conf = GripConfig(host=host, port=port)

    if vertex:
        for v in _getVertices(conf, graph, limit):
            click.echo(json.dumps(v, indent=2))

    if edge:
        for e in _getEdges(conf, graph, limit):
            click.echo(json.dumps(e, indent=2))


@grip.command(name="backup")
@grip_options
@dir_options
def backup_grip(host: str, port: int, graph: str, limit: int, vertex: bool, edge: bool, dir: Path):
    """grip ➜ local"""
    conf = GripConfig(host=host, port=port)

    # Set timestamp
    dir.mkdir(parents=True, exist_ok=True)

    logging.debug(f"Backing up GRIP graph '{graph}' to directory '{dir}'")
    _gripDump(conf, graph, limit, vertex, edge, dir)

    # TODO: Better way to handle GRIP graph schemas?
    schema = f"{graph}__schema__"
    logging.debug(f"Backing up GRIP graph '{schema}' to directory '{dir}'")
    _gripDump(conf, schema, limit, vertex, edge, dir)


@grip.command(name="restore")
@grip_options
@dir_options
def restore_grip(host: str, port: int, graph: str, dir: Path):
    """local ➜ grip"""
    conf = GripConfig(host=host, port=port)

    _ = _gripRestore(conf, graph, dir)


@cli.group(aliases=["pg"])
def pg():
    """Commands for Postgres backups."""
    pass


@pg.command(name="ls")
@pg_options
def listDbs(host: str, port: int, user: str, password: str):
    """list databases"""
    conf = PGConfig(host=host, port=port, user=user, password=password)

    dbs = _getDbs(conf)
    if not dbs:
        logging.warning(f"No databases found at {conf.host}:{conf.port}.")
        return

    # List databases
    for database in dbs:
        click.echo(database)


@pg.command(name="dump")
@pg_options
@dir_options
def dump_postgres(host: str, port: int, user: str, password: str, dir: Path):
    """postgres ➜ local"""
    conf = PGConfig(host=host, port=port, user=user, password=password)

    # Dump directory
    dir.mkdir(parents=True, exist_ok=True)

    dbs = _getDbs(conf)
    if not dbs:
        logging.warning(f"No databases found to dump at {conf.host}:{conf.port}.")
        return

    # Dump databases
    for database in dbs:
        dump = _pgDump(conf, database, dir)
        logging.debug(f"Dumped {database} to {dump}")


@pg.command(name="restore")
@pg_options
@dir_options
def restore_postgres(host: str, port: int, user: str, password: str, dir: Path):
    """local ➜ postgres"""
    conf = PGConfig(host=host, port=port, user=user, password=password)

    dbs = _getDbs(conf)
    if not dbs:
        logging.warning(f"No databases found to restore at {conf.host}:{conf.port}.")
        return

    # Restore databases
    for database in dbs:
        _ = _pgRestore(conf, database, dir)


@cli.group()
def s3():
    """Commands for S3."""
    pass


@s3.command()
@s3_options
@dir_options
def download(endpoint: str, bucket: str, key: str, secret: str, dir: Path):
    """s3 ➜ local"""
    conf = S3Config(endpoint=endpoint, bucket=bucket, key=key, secret=secret)

    # Download from S3
    _ = _download(conf, dir)


@s3.command()
@s3_options
@dir_options
def upload(endpoint: str, bucket: str, key: str, secret: str, dir: Path):
    """local ➜ s3"""
    s3 = S3Config(endpoint=endpoint, bucket=bucket, key=key, secret=secret)

    # Upload to S3
    _ = _upload(s3, dir)
