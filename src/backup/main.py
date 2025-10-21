from backup.elasticsearch import (
    ESConfig,
    _getIndices,
    _dump as _esDump,
    _restore as _esRestore,
    _getRepos,
    _initRepo,
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
    es_options,
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
    # ref: https://stackoverflow.com/a/47157553
    logging.getLogger("elastic_transport.transport").setLevel(logging.CRITICAL)
    warnings.simplefilter("ignore", ElasticsearchWarning)


if __name__ == "__main__":
    cli()



@cli.group(aliases=["es"])
def es():
    """Commands for ElasticSearch backups."""
    pass


@es.command(name="ls")
@es_options
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


@es.command(name="ls-repo")  # New command for listing repositories
@es_options
def listRepos(host: str, port: int, user: str, password: str):
    """list snapshot repositories"""
    esConfig = ESConfig(host=host, port=port, user=user, password=password)

    repos = _getRepos(esConfig)
    if not repos:
        logging.warning(
            f"No snapshot repositories found at {esConfig.host}:{esConfig.port}"
        )
        return

    # List repositories
    for repo in repos:
        click.echo(repo)


@es.command(name="init-repo")  # New command for initializing a repository
@es_options
@s3_options
@click.option(
    "--repo-name",
    "-r",
    required=True,
    help="Name of the Elasticsearch snapshot repository to initialize.",
)
def initRepo(
    host: str,
    port: int,
    user: str,
    password: str,
    repo_name: str,
    endpoint: str,
    bucket: str,
    key: str,
    secret: str,
):
    """initialize a snapshot repository"""
    # Create ElasticSearchConfig including S3 endpoint and bucket for repository creation
    esConfig = ESConfig(
        host=host,
        port=port,
        user=user,
        password=password,
        repo=repo_name,
        endpoint=endpoint,
        bucket=bucket,
    )

    success = _initRepo(esConfig)
    if success:
        click.echo(f"Repository '{repo_name}' initialized successfully.")
    else:
        logging.error(f"Failed to initialize repository '{repo_name}'.")


@es.command(name="backup")
@es_options
def backup_es(host: str, port: int, user: str, password: str):
    """elasticsearch ➜ local"""

    esConfig = ESConfig(host=host, port=port, user=user, password=password)
    indices = _getIndices(esConfig)
    if not indices:
        logging.warning(f"No indices found at {esConfig.host}:{esConfig.port}")
        return

    for index in indices:
        snapshot = _esDump(esConfig, index)
        logging.debug(f"Dumped index '{index}' to '{snapshot}'")


@es.command(name="restore")
@es_options
@dir_options
def restore_es(host: str, port: int, user: str, password: str, snapshot: str):
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


@grip.command(name="ls")
@grip_options
def list_grip(host: str, port: int, graph: str, vertex: bool, edge: bool):
    """list GRIP vertices and/or edges"""
    conf = GripConfig(host=host, port=port)

    if vertex:
        logging.debug(
            f"Listing vertices from GRIP graph '{graph}' at {conf.host}:{conf.port}"
        )
        for v in _getVertices(conf, graph):
            click.echo(json.dumps(v, indent=2))

    if edge:
        logging.debug(
            f"Listing edges from GRIP graph '{graph}' at {conf.host}:{conf.port}"
        )
        for e in _getEdges(conf, graph):
            click.echo(json.dumps(e, indent=2))


@grip.command(name="backup")
@grip_options
@dir_options
def backup_grip(host: str, port: int, graph: str, vertex: bool, edge: bool, dir: Path):
    """grip ➜ local"""
    conf = GripConfig(host=host, port=port)

    # Set timestamp
    dir.mkdir(parents=True, exist_ok=True)

    logging.debug(f"Backing up GRIP graph '{graph}' to directory '{dir}'")
    _gripDump(conf, graph, vertex, edge, dir)

    # TODO: Better way to handle GRIP graph schemas?
    schema = f"{graph}__schema__"
    logging.debug(f"Backing up GRIP graph '{schema}' to directory '{dir}'")
    _gripDump(conf, schema, vertex, edge, dir)


@grip.command(name="restore")
@grip_options
@dir_options
def restore_grip(host: str, port: int, graph: str, vertex: bool, edge: bool, dir: Path):
    """local ➜ grip"""
    conf = GripConfig(host=host, port=port)

    _ = _gripRestore(conf, graph, dir)


@cli.group(aliases=["pg"])
def pg():
    """Commands for Postgres backups."""
    pass


@pg.command(name="ls")
@pg_options
def listDbs(host: str, port: int, user: str):
    """list databases"""
    conf = PGConfig(host=host, port=port, user=user)

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
def dump_postgres(host: str, port: int, user: str, dir: Path):
    """postgres ➜ local"""
    conf = PGConfig(host=host, port=port, user=user)

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
def restore_postgres(host: str, port: int, user: str, dir: Path):
    """local ➜ postgres"""
    conf = PGConfig(host=host, port=port, user=user)

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
