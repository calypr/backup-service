from backup.elasticsearch import (
    ESConfig,
    _getIndices,
    _dump as _esDump,
    _restore as _esRestore,
)
from . import ESConfig, es_flags
from .repo.cli import repo, repo_flags
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
@repo_flags
def backup(host: str, port: int, repo: str, endpoint: str, bucket: str):
    """elasticsearch ➜ local"""

    esConfig = ESConfig(
        host=host,
        port=port,
        repo=repo,
        endpoint=endpoint,
        bucket=bucket,
    )

    indices = _getIndices(esConfig)
    if not indices:
        logging.warning(f"No indices found at {esConfig.host}:{esConfig.port}")
        return

    for index in indices:
        logging.debug(f"Backing up index '{index}'") 
        snapshot = _esDump(esConfig, index)
        logging.debug(f"Dumped index '{index}' to '{snapshot}'")


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
        _ = _esRestore(esConfig, index, snapshot)


# Elasticsearch snapshot repository commands
es.add_command(repo)
