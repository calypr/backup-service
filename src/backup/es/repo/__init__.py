import logging
from backup.es import ESConfig, _connect


def _getRepos(esConfig: ESConfig) -> list[str] | None:
    """
    Utility function to connect to ElasticSearch and list all snapshot repositories.
    """
    elastic = _connect(esConfig)

    try:
        repos = elastic.snapshot.get_repository(name="_all")  # Get all repositories
        repo_names = list(repos.keys())  # Extract just the names
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
        repository={
            "type": "s3",
            "settings": {
                "bucket": esConfig.bucket,
                "base_path": esConfig.repo,
            },
        },
    )

    logging.info(f"Repository '{esConfig.repo}' created successfully.")

    return True


def _deleteRepo(esConfig: ESConfig, force: bool) -> bool:
    """
    Initializes a snapshot repository in ElasticSearch.
    """
    if not force:
        logging.error("Deletion of repository requires --force flag.")
        return False

    elastic = _connect(esConfig)

    # Create the repository
    elastic.snapshot.delete_repository(
        name=esConfig.repo,
    )

    logging.info(f"Repository '{esConfig.repo}' deleted successfully.")

    return True
