import pytest
from backup.elasticsearch import (
    ElasticSearchConfig,
    _getIndices,
    _dump as _esDump,
    _restore as _esRestore,
)
from backup.postgres import (
    PostgresConfig,
    _getDbs,
    _dump as _pgDump,
    _restore as _pgRestore,
)
from backup.s3 import (
    S3Config,
    _download,
    _upload,
)


def testConnect(testPostgres):
    """
    Tests connecting to the database.
    """
    print(f"Test received database URL: {testPostgres}")

    connection = _connect(testPostgres)

    # TODO: Improve test
    assert connection is not None


def testListDbs(testPostgres):
    """
    Tests listing databases in the PostgreSQL server.
    """
    connection = _connect(testPostgres)
    dbs = _listDbs(connection)

    # TODO: Improve test
    assert isinstance(dbs, list)


def testDump(testPostgres, tmp_path):
    """
    Tests creating a dump of a specific database.
    """

    connection = _connect(testPostgres)
    dbs = _listDbs(connection)
    dir = _dump(testPostgres, "postgres", tmp_path)

    # TODO: Improve test
    assert dir.is_dir(), "Dump directory should be created"


def testUpload(testS3, testDir):
    """
    Tests uploading database dump to S3.
    """

    err = _upload(testS3, testDir)

    # TODO: Improve test
    assert err is None, "Error uploading to S3"


def testDownload(testS3, tmp_path):
    """
    Tests downloading database dump from S3.
    """

    err = _download(testS3, tmp_path)

    # TODO: Improve test
    assert err is None, "Error downloading from S3"


def testRestore(testPostgres, tmp_path):
    """
    Tests restoring a database from a dump.
    """
    pass


def testGetDbs(testPostgres):
    """
    Tests retrieving the names of all databases in the PostgreSQL server.
    """
    pass
