from dataclasses import dataclass
import logging
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
    endpoint: str = ""


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
    Utiltity function to connect to ElasticSearch and list all indices.
    """
    elastic = _connect(esConfig)

    # Get all indices using the cat.indices() method
    indices = elastic.cat.indices(h="index").splitlines()

    return indices


def _dump(esConfig: ESConfig, index: str) -> str | None:
    """
    Creates a snapshot of a single index using Elasticsearch Snapshot API.
    """
    elastic = _connect(esConfig)

    # Check if index exists before attempting to snapshot
    if not elastic.indices.exists(index=index):
        logging.warning(f"Index '{index}' not found")

    response = elastic.snapshot.create(
        repository=esConfig.repo,
        snapshot=index,
        wait_for_completion=True,
    )

    if response["snapshot"]["state"] == "SUCCESS":
        return response["snapshot"]["snapshot_id"]
    else:
        logging.error(f"Snapshot '{index}' error: {response}")


def _restore(esConfig: ESConfig, index: str, snapshot: str) -> bool:
    """
    Restores a single index from a snapshot using Elasticsearch Snapshot API.
    """
    elastic = _connect(esConfig)
    if elastic is None:
        return False

    # Check if the snapshot exists
    snapshot_info = elastic.snapshot.get(repository=esConfig.repo, snapshot=snapshot)
    if not snapshot_info["snapshots"]:
        logging.error(f"Snapshot '{snapshot}' not found in repo '{esConfig.repo}'")
        return False

    # Close the index before restoring
    if elastic.indices.exists(index=index):
        elastic.indices.close(index=index)

    response = elastic.snapshot.restore(
        repository=esConfig.repo,
        snapshot=snapshot,
        body={"indices": index},
        wait_for_completion=True,
    )

    if response["snapshot"]["state"] == "SUCCESS":
        return True

    else:
        logging.error(f"Snapshot '{snapshot}' error: {response}")
        return False
