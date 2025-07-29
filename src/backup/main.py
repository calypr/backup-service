from backup.elasticsearch import (
    ESConfig,
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
    elasticsearch_options,
    postgres_options,
    s3_options,
)
from click_aliases import ClickAliasedGroup
from datetime import datetime
from elasticsearch.exceptions import ElasticsearchWarning
from pathlib import Path
import click
import logging
import warnings


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
    # Default logging level is INFO
    level = logging.INFO

    # If the flag is provided set logging level to DEBUG
    if verbose:
        level = logging.DEBUG

    logging.basicConfig(
        level=level,
        format="%(asctime)s - %(levelname)s - %(message)s",
    )

    # Avoid INFO and ElasticsearchWarning logging from the elasticsearch logger
    logging.getLogger("elastic_transport.transport").setLevel(logging.CRITICAL)
    warnings.simplefilter("ignore", ElasticsearchWarning)


if __name__ == "__main__":
    cli()


@cli.group(aliases=["es"])
def elasticsearch():
    """Commands for ElasticSearch backups."""
    pass


@elasticsearch.command(name="ls")
@elasticsearch_options
def listIndices(host: str, port: int, user: str, password: str):
    """list indices"""
    esConfig = ESConfig(host=host, port=port, user=user, password=password)

    indices = _getIndices(esConfig)
    if not indices:
        logging.warning(f"No indices found at {esConfig.host}:{esConfig.port}")
        return

    # List indices
    for index in indices:
        click.echo(index)


@elasticsearch.command(name="backup")
@elasticsearch_options
@dir_options
def backup_elasticsearch(host: str, port: int, user: str, password: str, dir: Path):
    """elasticsearch ➜ local"""

    esConfig = ESConfig(host=host, port=port, user=user, password=password)
    indices = _getIndices(esConfig)
    if not indices:
        logging.warning(f"No indices found at {esConfig.host}:{esConfig.port}")
        return


@elasticsearch.command(name="restore")
@elasticsearch_options
@dir_options
def restore_elasticsearch(
    host: str, port: int, user: str, password: str, snapshot: str
):
    """local ➜ elasticsearch"""
    esConfig = ESConfig(host=host, port=port, user=user, password=password)

    indices = _getIndices(esConfig)
    if not indices:
        logging.warning(
            f"No indices found to restore at {esConfig.host}:{esConfig.port}."
        )
        return

    # Restore indices
    for index in indices:
        _ = _esRestore(esConfig, index, snapshot)


@cli.group(aliases=["gp"])
def grip():
    """Commands for GRIP backups."""
    pass


@cli.group(aliases=["pg"])
def postgres():
    """Commands for Postgres backups."""
    pass


@postgres.command(name="ls")
@postgres_options
def listDbs(host: str, port: int, user: str, password: str):
    """list databases"""
    p = PGConfig(host=host, port=port, user=user, password=password)

    dbs = _getDbs(p)
    if not dbs:
        logging.warning(f"No databases found at {p.host}:{p.port}.")
        return

    # List databases
    for database in dbs:
        click.echo(database)


@postgres.command(name="dump")
@postgres_options
@dir_options
def dump_postgres(host: str, port: int, user: str, password: str, dir: Path):
    """postgres ➜ local"""
    p = PGConfig(host=host, port=port, user=user, password=password)

    # Shared timestamp for all dumps
    timestamp = datetime.now().isoformat()

    # Dump directory
    out = dir / Path(timestamp)
    out.mkdir(parents=True, exist_ok=True)

    dbs = _getDbs(p)
    if not dbs:
        logging.warning(f"No databases found to dump at {p.host}:{p.port}.")
        return

    # Dump databases
    for database in dbs:
        dump = _pgDump(p, database, out)
        logging.debug(f"Dumped {database} to {dump}")


@postgres.command(name="restore")
@postgres_options
@dir_options
def restore_postgres(host: str, port: int, user: str, password: str, dir: Path):
    """local ➜ postgres"""
    p = PGConfig(host=host, port=port, user=user, password=password)

    dbs = _getDbs(p)
    if not dbs:
        logging.warning(f"No databases found to restore at {p.host}:{p.port}.")
        return

    # Restore databases
    for database in dbs:
        _ = _pgRestore(p, database, dir)


@cli.group()
def s3():
    """Commands for S3."""
    pass

@s3.command()
@s3_options
@dir_options
def download(endpoint: str, bucket: str, key: str, secret: str, dir: Path):
    """s3 ➜ local"""
    s3 = S3Config(endpoint=endpoint, bucket=bucket, key=key, secret=secret)

    # Download from S3
    _ = _download(s3, dir)


@s3.command()
@s3_options
@dir_options
def upload(endpoint: str, bucket: str, key: str, secret: str, dir: Path):
    """local ➜ s3"""
    s3 = S3Config(endpoint=endpoint, bucket=bucket, key=key, secret=secret)

    # Upload to S3
    _ = _upload(s3, dir)
