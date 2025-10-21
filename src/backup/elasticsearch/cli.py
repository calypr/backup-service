from backup.elasticsearch import (
    ESConfig,
    _getIndices,
    _dump as _esDump,
    _restore as _esRestore,
    _getRepos,
    _initRepo,
)
from backup.options import (
    dir_options,
    es_options,
    s3_options,
)
import click
import logging


@click.group()
def es():
    """Commands for ElasticSearch backups."""
    pass


@es.command()
@es_options
def ls(host: str, port: int, user: str, password: str):
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


@es.command()
@es_options
def backup(host: str, port: int, user: str, password: str):
    """elasticsearch ➜ local"""

    esConfig = ESConfig(host=host, port=port, user=user, password=password)
    indices = _getIndices(esConfig)
    if not indices:
        logging.warning(f"No indices found at {esConfig.host}:{esConfig.port}")
        return

    for index in indices:
        snapshot = _esDump(esConfig, index)
        logging.debug(f"Dumped index '{index}' to '{snapshot}'")


@es.command()
@es_options
@dir_options
def restore(host: str, port: int, user: str, password: str, snapshot: str):
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
