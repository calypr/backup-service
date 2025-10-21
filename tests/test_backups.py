import pytest
from backup.grip import (
    GripConfig,
    _getEdges,
    _getVertices,
    _dump as _gripDump,
    _restore as _gripRestore,
)
from backup.postgres import (
    PGConfig,
    _connect,
    _getDbs,
    _dump as _pgDump,
    _restore as _pgRestore,
)
from backup.s3 import (
    S3Config,
    _download,
    _upload,
)
from backup.options import (
    dir_options,
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
    dbs = _getDbs(testPostgres)

    # TODO: Improve test
    assert isinstance(dbs, list)


@pytest.mark.skip(reason="TODO: Implement")
def testDump(testPostgres, tmp_path):
    """
    Tests creating a dump of a specific database.
    """

    _ = _connect(testPostgres)
    _ = _getDbs(testPostgres)
    dir = _pgDump(testPostgres, "postgres", tmp_path)

    # TODO: Improve test
    assert dir is not None, "Dump directory should be created"


@pytest.mark.skip(reason="TODO: Implement")
def testUpload(testS3, testDir):
    """
    Tests uploading database dump to S3.
    """

    err = _upload(testS3, testDir)

    # TODO: Improve test
    assert err is None, "Error uploading to S3"


@pytest.mark.skip(reason="TODO: Implement")
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
