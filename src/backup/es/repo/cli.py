import logging
import click
from .. import ESConfig, es_flags
from ..repo import _deleteRepo, _getRepos, _initRepo
from backup.s3.cli import s3_flags


# ElasticSearch Flags
def es_repo_flags(fn):
    options = [
        click.option(
            "--repo",
            "-r",
            envvar="ES_REPO",
            show_default=True,
            help="ElasticSearch snapshot repository name ($ES_REPO)",
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
    """List snapshot repositories"""
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
@es_repo_flags
@s3_flags
def initRepo(host: str, port: int, repo: str, endpoint: str, bucket: str):
    """Initialize a snapshot repository"""

    # Create ElasticSearchConfig including S3 endpoint and bucket for repository creation
    esConfig = ESConfig(
        host=host,
        port=port,
        repo=repo,
        endpoint=endpoint,
        bucket=bucket,
    )

    # TODO: Add readonly flag to for restore operations
    success = _initRepo(esConfig)
    if success:
        click.echo(f"Repository '{repo}' initialized successfully.")
    else:
        logging.error(f"Failed to initialize repository '{repo}'.")


@repo.command(name="rm")
@es_flags
@es_repo_flags
@click.option(
    "--force",
    is_flag=True,
    default=False,
    help="Force/confirm deletion of the repository.",
)
def deleteRepo(host: str, port: int, repo: str, force: bool):
    """Initialize a snapshot repository"""
    # Create ElasticSearchConfig including S3 endpoint and bucket for repository creation
    esConfig = ESConfig(
        host=host,
        port=port,
        repo=repo,
    )

    success = _deleteRepo(esConfig, force)
    if success:
        click.echo(f"Repository '{repo}' deleted successfully.")
    else:
        logging.error(f"Failed to delete repository '{repo}'.")
