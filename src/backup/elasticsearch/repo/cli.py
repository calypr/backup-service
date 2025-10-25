import logging
import click
from .. import ESConfig, es_flags
from ..repo import _getRepos, _initRepo
from backup.s3.cli import s3_flags


# ElasticSearch Flags
def repo_flags(fn):
    options = [
        click.option(
            "--repo",
            "-r",
            envvar="ES_REPO",
            default="backup_repo",
            show_default=True,
            help="ElasticSearch snapshot repository name ($ES_REPO)",
        ),
        click.option(
            "--bucket",
            "-b",
            envvar="ES_BUCKET",
            default="backup_bucket",
            show_default=True,
            help="S3 bucket name for ElasticSearch backups ($ES_BUCKET)",
        ),
        click.option(
            "--endpoint",
            "-e",
            envvar="ES_ENDPOINT",
            default="https://s3.amazonaws.com",
            show_default=True,
            help="S3 endpoint URL for ElasticSearch backups ($ES_ENDPOINT)",
        ),
    ]
    for option in reversed(options):
        fn = option(fn)
    return fn


@click.group()
def repo():
    """Commands for managing snapshot repositories."""
    pass


@repo.command(name="ls")
@es_flags
def listRepos(host: str, port: int):
    """list snapshot repositories"""
    esConfig = ESConfig(host=host, port=port)

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
@es_flags
@repo_flags
def initRepo(
    host: str,
    port: int,
    repo: str,
    endpoint: str,
    bucket: str,
):
    """initialize a snapshot repository"""
    # Create ElasticSearchConfig including S3 endpoint and bucket for repository creation
    esConfig = ESConfig(
        host=host,
        port=port,
        repo=repo,
        endpoint=endpoint,
        bucket=bucket,
    )

    success = _initRepo(esConfig)
    if success:
        click.echo(f"Repository '{repo}' initialized successfully.")
    else:
        logging.error(f"Failed to initialize repository '{repo}'.")
