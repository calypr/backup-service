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
@click.option(
    "--vertex", "--vertices", "-v", is_flag=True, help="Only list GRIP vertices."
)
@click.option("--edge", "--edges", "-e", is_flag=True, help="Only list GRIP edges.")
def list_grip(host: str, port: int, vertex: bool, edge: bool):
    """list GRIP vertices and/or edges"""
    g = GripConfig(host=host, port=port)

    show_vertices = vertex or not (vertex or edge)
    show_edges = edge or not (vertex or edge)

    if show_vertices:
        verts = _getVertices(g)
        if not verts:
            logging.warning(f"No vertices found at {g.host}:{g.port}")
        else:
            for vertex in verts:
                click.echo(vertex)

    if show_edges:
        eds = _getEdges(g)
        if not eds:
            logging.warning(f"No edges found at {g.host}:{g.port}")
        else:
            for edge in eds:
                click.echo(edge)


@grip.command(name="backup")
@grip_options
@dir_options
def backup_grip(host: str, port: int, dir: Path):
    """grip ➜ local"""
    conf = GripConfig(host=host, port=port)

    # Shared timestamp for all dumps
    timestamp = datetime.now().isoformat()
    out = dir / Path(timestamp)
    out.mkdir(parents=True, exist_ok=True)

    _gripDump(conf, out)


@grip.command(name="restore")
@grip_options
@dir_options
def restore_grip(host: str, port: int, user: str, password: str, dir: Path):
    """local ➜ grip"""
    pass


@cli.group(aliases=["pg"])
def pg():
    """Commands for Postgres backups."""
    pass


@pg.command(name="ls")
@pg_options
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


@pg.command(name="dump")
@pg_options
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


@pg.command(name="restore")
@pg_options
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
