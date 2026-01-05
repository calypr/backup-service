from dataclasses import dataclass
import logging
import sys
import click
from elasticsearch import Elasticsearch


# ElasticSearch Flags
def es_flags(fn):
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
    ]
    for option in reversed(options):
        fn = option(fn)
    return fn


@dataclass
class ESConfig:
    """ElasticSearch config"""

    host: str
    port: int

    # Backup repo
    # https://www.elastic.co/docs/deploy-manage/tools/snapshot-and-restore/self-managed
    repo: str = ""
    bucket: str = ""


def _connect(esConfig: ESConfig) -> Elasticsearch:
    """
    Connects to a given ElasticSearch instance.
    """
    assert esConfig.host, "Host must not be empty"
    assert esConfig.port, "Port must not be empty"

    try:
        elastic = Elasticsearch(
            hosts=[{"host": esConfig.host, "port": esConfig.port, "scheme": "http"}],
        )
    except Exception as err:
        logging.error(f"Error connecting to Elasticsearch: {err}")
        raise

    return elastic


def _getIndices(esConfig: ESConfig) -> list[str]:
    """
    Utiltity function to list all indices.
    """
    elastic = _connect(esConfig)

    # Get all indices using the cat.indices() method
    indices = elastic.cat.indices(h="index").splitlines()

    # Remove unused '.geoip_databases' to avoid `400` error during snapshot
    # https://www.elastic.co/docs/reference/enrich-processor/geoip-processor
    if ".geoip_databases" in indices:
        indices.remove(".geoip_databases")

    return indices


def _getRepos(esConfig: ESConfig) -> list[str]:
    """
    Utiltity function to list all repos
    """
    elastic = _connect(esConfig)

    repos = elastic.cat.repositories().splitlines()

    return repos


def _getSnapshots(esConfig: ESConfig, repo: str) -> list[str]:
    """
    Utiltity function to list all snapshots in a given repository.
    """
    elastic = _connect(esConfig)

    snapshots = elastic.snapshot.get(
        repository=repo,
        snapshot="_all",
    )["snapshots"]

    snapshot_names = [snap["snapshot"] for snap in snapshots]

    return snapshot_names


def _getSnapshotIndices(esConfig: ESConfig, repo: str, snapshot: str) -> list[str]:
    """
    Utiltity function to list all indices in all snapshots in a given repository.
    """
    elastic = _connect(esConfig)

    snapshots = elastic.snapshot.get(
        repository=repo,
        snapshot=snapshot,
    )["snapshots"]

    indices = []
    for snap in snapshots:
        indices.extend(snap.get("indices", []))
    
    # Remove unused '.geoip_databases' to avoid `400` error during snapshot
    # https://www.elastic.co/docs/reference/enrich-processor/geoip-processor
    if ".geoip_databases" in indices:
        indices.remove(".geoip_databases")

    return indices


def _snapshot(esConfig: ESConfig, indices: list[str], snapshot: str) -> str | None:
    """
    Creates a snapshot of indices using Elasticsearch Snapshot API.
    """
    elastic = _connect(esConfig)

    response = elastic.snapshot.create(
        # Snapshot repo
        repository=esConfig.repo,
        # Timestamp
        snapshot=snapshot,
        # Indices to backup
        indices=indices,
        # Block until complete
        wait_for_completion=True,
    )

    logging.debug(f"Snapshot response: {response}")

    if response["snapshot"]["state"] == "SUCCESS":
        # TODO: Return more useful info here?
        return response["snapshot"]["snapshot"]
    else:
        logging.error(f"Snapshot error: {response}")


def _restore(esConfig: ESConfig, indices: list[str], snapshot: str) -> str | None:
    """
    Restores a single index from a snapshot using Elasticsearch Snapshot API.
    If the indices do not exist, they will be created before restoring.
    """
    elastic = _connect(esConfig)

    # Check if indices exist
    existing_indices = _getIndices(esConfig)

    for index in indices:
        if index not in existing_indices:
            # Create the index if it doesn't exist
            logging.info(f"Index '{index}' does not exist. Creating it before restore.")
            elastic.indices.create(index=index)

    # Close indices before restore
    elastic.indices.close(index=",".join(indices))

    response = elastic.snapshot.restore(
        repository=esConfig.repo,
        snapshot=snapshot,
        indices=indices,
        wait_for_completion=True,
    )

    logging.debug(f"Restore response: {response}")

    if response["snapshot"]["state"] == "SUCCESS":
        # TODO: Return more useful info here?
        return response["snapshot"]["snapshot"]

    else:
        logging.error(f"Snapshot '{snapshot}' error: {response}")
