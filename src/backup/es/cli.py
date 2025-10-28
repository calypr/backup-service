from datetime import datetime
from backup.es import (
    ESConfig,
    _getIndices,
    _snapshot,
    _restore,
)
from . import ESConfig, es_flags
from .repo.cli import repo, es_repo_flags
from backup.options import (
    dir_flags,
)
import click
import logging


@click.group()
def es():
    """Commands for ElasticSearch backups."""
    pass


@es.command()
@es_flags
def ls(host: str, port: int):
    """list indices"""
    esConfig = ESConfig(host=host, port=port)

    indices = _getIndices(esConfig)
    if not indices:
        logging.warning(f"No indices found at {esConfig.host}:{esConfig.port}")
        return

    # List indices
    for index in indices:
        click.echo(index)


@es.command()
@es_flags
@es_repo_flags
@click.option(
    "--snapshot",
    "-s",
    required=True,
    default=lambda: datetime.now().strftime('%Y-%m-%d_%H-%M-%S'),
    help="Snapshot name (will be created under the repository)",
)
def backup(host: str, port: int, repo: str, snapshot: str):
    """elasticsearch ➜ local"""

    esConfig = ESConfig(
        host=host,
        port=port,
        repo=repo,
    )

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
@dir_flags
def restore(host: str, port: int, snapshot: str):
    """local ➜ elasticsearch"""
    esConfig = ESConfig(host=host, port=port)

    indices = _getIndices(esConfig)
    if not indices:
        logging.warning(
            f"No indices found to restore at {esConfig.host}:{esConfig.port}."
        )
        return

    # Restore indices
    for index in indices:
        _ = _restore(esConfig, index, snapshot)


# Elasticsearch snapshot repository commands
es.add_command(repo)
