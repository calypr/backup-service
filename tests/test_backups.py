from backup import (
    S3Config,
    connect,
    dumpDbs,
    listDbs,
    upload,
)
from pathlib import Path


def testConnect(testPostgres):
    """
    Tests connecting to the database.
    """
    print(f"Test received database URL: {testPostgres}")

    connection = connect(testPostgres)

    # TODO: Improve test
    assert connection is not None


def testListDbs(testPostgres):
    """
    Tests listing databases in the PostgreSQL server.
    """
    connection = connect(testPostgres)
    dbs = listDbs(connection)

    # TODO: Improve test
    assert isinstance(dbs, list)


def testDumpDb(testPostgres):
    """
    Tests creating a dump of a specific database.
    """

    connection = connect(testPostgres)
    dbs = listDbs(connection)
    dir = dumpDbs(testPostgres, dbs)

    # TODO: Improve test
    assert dir.is_dir(), "Dump directory should be created"


def testUpload():
    """
    Tests uploading database dump to S3.
    """

    # TODO: Add test S3 configuration
    err = upload(testS3, testDir)

    # TODO: Improve test
    assert err is None, "Upload should not return an error"
