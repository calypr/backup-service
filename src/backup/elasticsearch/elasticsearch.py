from dataclasses import dataclass
import logging
from pathlib import Path
import subprocess
from elasticsearch import Elasticsearch


@dataclass
class ElasticSearchConfig:
    """ElasticSearch config"""

    host: str
    port: int
    user: str
    password: str
    # Backup repo
    # https://www.elastic.co/docs/deploy-manage/tools/snapshot-and-restore/self-managed
    repo: str = ""


def _connect(esConfig: ElasticSearchConfig) -> Elasticsearch:
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


def _getIndices(esConfig: ElasticSearchConfig) -> list[str] | None:
    """
    Utiltity function to connect to ElasticSearch and list all indices.
    """
    elastic = _connect(esConfig)

    # Get all indices using the cat.indices() method
    indices = elastic.cat.indices(h="index").splitlines()

    return indices


def _initRepo(esConfig: ElasticSearchConfig) -> bool:
    """
    Initializes a snapshot repository in ElasticSearch.
    """
    elastic = _connect(esConfig)

    # Check if the repository already exists
    if elastic.snapshot.get_repository(name=esConfig.repo):
        logging.debug(f"Repository '{esConfig.repo}' already exists.")
        return True

    # Create the repository
    elastic.snapshot.create_repository(
        name=esConfig.repo,
        body={
            "type": "s3",
            "bucket": esConfig.repo,
            "access_key": esConfig.user,
            "secret_key": esConfig.password,
            "base_path": "elasticsearch",
            "endpoint": "s3.amazonaws.com",
        },
    )
    logging.info(f"Repository '{esConfig.repo}' created successfully.")
    return True


def _dump(esConfig: ElasticSearchConfig, index: str, snapshot_id: str) -> str | None:
    """
    Creates a snapshot of a single index using Elasticsearch Snapshot API.
    """
    elastic = _connect(esConfig)

    # Check if index exists before attempting to snapshot
    if not elastic.indices.exists(index=index):
        logging.warning(f"Index '{index}' not found")
        return None

    response = elastic.snapshot.create(
        repository=esConfig.repo,
        snapshot=snapshot_id,
        body={"indices": index, "include_global_state": False},
        wait_for_completion=True,
    )

    if response["snapshot"]["state"] == "SUCCESS":
        return snapshot_id
    else:
        logging.error(f"Snapshot '{index}:{snapshot_id}' error: {response}")
        return None


def _restore(esConfig: ElasticSearchConfig, index: str, snapshot: str) -> bool:
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
