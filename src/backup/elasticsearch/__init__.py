from dataclasses import dataclass
import logging
from pathlib import Path
import subprocess
from elasticsearch import Elasticsearch


@dataclass
class ESConfig:
    """ElasticSearch config"""

    host: str
    port: int
    user: str
    password: str
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

def _getRepos(esConfig: ESConfig) -> list[str] | None:
    """
    Utility function to connect to ElasticSearch and list all snapshot repositories.
    """
    elastic = _connect(esConfig)
    
    try:
        repos = elastic.snapshot.get_repository(name="_all") # Get all repositories
        repo_names = list(repos.keys()) # Extract just the names
        return repo_names
    except Exception as err:
        logging.error(f"Error listing Elasticsearch repositories: {err}")
        return None


def _initRepo(esConfig: ESConfig) -> bool:
    """
    Initializes a snapshot repository in ElasticSearch.
    """
    elastic = _connect(esConfig)

    # Create the repository
    elastic.snapshot.create_repository(
        name=esConfig.repo,
        body={
            "type": "s3",
            "endpoint": esConfig.endpoint,
            "bucket": esConfig.bucket,
            "base_path": esConfig.repo,
            "access_key": esConfig.user,
            "secret_key": esConfig.password,
        },
    )
    logging.info(f"Repository '{esConfig.repo}' created successfully.")
    return True


def _dump(esConfig: ESConfig, index: str):
    """
    Creates a snapshot of a single index using Elasticsearch Snapshot API.
    """
    elastic = _connect(esConfig)

    # Check if index exists before attempting to snapshot
    if not elastic.indices.exists(index=index):
        logging.warning(f"Index '{index}' not found")

    response = elastic.snapshot.create(
        repository=esConfig.repo,
        snapshot=f"{index}",
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
