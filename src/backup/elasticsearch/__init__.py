from dataclasses import dataclass
import logging
from pathlib import Path
from elasticsearch import Elasticsearch


@dataclass
class ElasticSearchConfig:
    """ElasticSearch config"""

    host: str
    port: int
    user: str
    password: str


def _connect(esConfig: ElasticSearchConfig) -> Elasticsearch:
    """
    Connects to a given ElasticSearch instance.
    """
    assert esConfig.host, "Host must not be empty"
    assert esConfig.port, "Port must not be empty"
    assert esConfig.user, "User must not be empty"
    assert esConfig.password, "Password must not be empty"

    try:
        elastic = Elasticsearch(
            hosts=[{"host": esConfig.host, "port": esConfig.port}],
            http_auth=(esConfig.user, esConfig.password)
        )
    except Exception as err:
        logging.error(f"Error connecting to Elasticsearch: {err}")
        raise

    return elastic


def _getIndices(esConfig: ElasticSearchConfig) -> list[str] | None:
    """
    Utiltity function to connect to ElasticSearch and list all indices.
    """

    return None


def _listIndices(elastic: Elasticsearch) -> list[str] | None:
    """
    Retrieves the names of all indices in the ElasticSearch server.
    """
    
    # Return indices
    return None


def _dump(esConfig: ElasticSearchConfig, database: str, dir: Path) -> Path | None:
    """
    Creates a single database dump.
    """

    return None 


def _restore(esConfig: ElasticSearchConfig, database: str, dir: Path) -> Path | None:
    """
    Restores a single database from a dump file.
    """
    
    return None
