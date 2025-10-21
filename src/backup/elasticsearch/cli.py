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
)
from backup.s3.cli import (
    s3_options,
    S3Config,
)
import click
import logging


# ElasticSearch Flags
def es_options(fn):
    options = [
        click.option(
            "--host",
            "-H",
            envvar="ES_HOST",
            default="localhost",
            show_default=True,
            help="ElasticSearch host ($ES_HOST)",
        ),
        click.option(
            "--port",
            "-p",
            envvar="ES_PORT",
            default=9200,
            show_default=True,
            help="ElasticSearch port ($ES_PORT)",
        ),
        click.option(
            "--user",
            "-u",
            envvar="ES_USER",
            default="elastic",
            show_default=True,
            help="ElasticSearch username ($ES_USER)",
        ),
        click.option(
            "--password",
            "-P",
            envvar="ES_PASSWORD",
            help="ElasticSearch password ($ES_PASSWORD)",
        ),
        # click.option(
        #     "--repo",
        #     "-r",
        #     envvar="ES_REPO",
        #     default="backup_repo",
        #     show_default=True,
        #     help="ElasticSearch snapshot repository name ($ES_REPO)",
        # ),
        # click.option(
        #     "--bucket",
        #     "-b",
        #     envvar="ES_BUCKET",
        #     default="backup_bucket",
        #     show_default=True,
        #     help="S3 bucket name for ElasticSearch backups ($ES_BUCKET)",
        # ),
        # click.option(
        #     "--endpoint",
        #     "-e",
        #     envvar="ES_ENDPOINT",
        #     default="https://s3.amazonaws.com",
        #     show_default=True,
        #     help="S3 endpoint URL for ElasticSearch backups ($ES_ENDPOINT)",
        # ),
    ]
    for option in reversed(options):
        fn = option(fn)
    return fn


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


@es.group()
def repo():
    """Commands for managing snapshot repositories."""
    pass


@repo.command(name="ls")
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


@repo.command(name="init")
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

