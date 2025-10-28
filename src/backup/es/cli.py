from datetime import datetime
from backup.es import (
    ESConfig,
    _getIndices,
    _getRepos,
    _getSnapshots,
    _getSnapshotIndices,
    _snapshot,
    _restore,
)
from . import ESConfig, es_flags
from .repo.cli import repo, es_repo_flags
import click
import logging


@click.group()
def es():
    """Commands for ElasticSearch backups."""
    pass


@es.command()
@es_flags
@click.option(
    "--repos",
    is_flag=True,
    default=False,
    help="List all snapshot repositories instead of indices",
)
@click.option(
    "--repo",
    default=None,
    help="Specify a repository to list its indices",
)
@click.option(
    "--snapshot",
    default=None,
    help="Specify a snapshot to list its indices",
)
# TODO: Fix spaghetti code
def ls(host: str, port: int, repos: bool, repo: str, snapshot: str):
    """List live indices, snapshot repositories, indices of a specific repository, or indices in a snapshot"""
    esConfig = ESConfig(host=host, port=port)

    # List repos in current cluster
    if repos:
        all_repos = _getRepos(esConfig)

        for repository in all_repos:
            click.echo(repository)

    # List indices in given snapshot
    elif repo and snapshot:
        indices = _getSnapshotIndices(esConfig, repo, snapshot)

        for index in indices:
            click.echo(index)

    # List snapshots in given repo
    elif repo:
        snapshots = _getSnapshots(esConfig, repo)

        for snapshot in snapshots:
            click.echo(snapshot)

    # List indices in current cluster
    else:
        indices = _getIndices(esConfig)

        for index in indices:
            click.echo(index)


@es.command()
@es_flags
@es_repo_flags
@click.option(
    "--snapshot",
    "-s",
    required=True,
    default=lambda: datetime.now().strftime("%Y-%m-%d_%H-%M-%S"),
    help="Snapshot name (will be created under the repository)",
)
def backup(host: str, port: int, repo: str, snapshot: str):
    """elasticsearch ➜ snapshot"""
    esConfig = ESConfig(host=host, port=port, repo=repo)

    indices = _getIndices(esConfig)
    if not indices:
        logging.warning(f"No indices found at {esConfig.host}:{esConfig.port}")
        return

    logging.debug(f"Backing up indices '{indices}' to snapshot '{snapshot}'")
    resp = _snapshot(esConfig, indices, snapshot)
    if resp:
        logging.info(f"Snapshot created: {resp}")
    else:
        logging.error("Snapshot creation failed")


@es.command()
@es_flags
@es_repo_flags
@click.option(
    "--snapshot",
    "-s",
    required=True,
    help="Snapshot name to restore from",
)
def restore(host: str, port: int, repo: str, snapshot: str):
    """snapshot ➜ elasticsearch"""
    esConfig = ESConfig(host=host, port=port, repo=repo)

    indices = _getSnapshotIndices(esConfig, repo, snapshot)
    if not indices:
        logging.warning(
            f"No indices found to restore at {esConfig.host}:{esConfig.port}."
        )
        return

    # Restore indices
    _ = _restore(esConfig, indices, snapshot)


# Elasticsearch snapshot repository commands
es.add_command(repo)
