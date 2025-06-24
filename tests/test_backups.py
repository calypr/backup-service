from backup import connect, dump, upload


# --- Example of how to use the fixture in a test ---
def test_connection(test_database):
    """
    Tests connecting to the database.
    """
    print(f"Test received database URL: {test_database}")
    connection = connect(
        host=test_database.host,
        user=test_database.user,
        password=test_database.password,
    )

    assert connection is not None


def test_dump(test_database):
    """
    Tests creating a database dump.
    """
    dump_file = dump(connection)
    assert dump_file is not None


def test_upload(test_database):
    """
    Tests uploading database dump to S3.
    """
    connection = connect(
        host=test_database.host,
        user=test_database.user,
        password=test_database.password,
    )
    assert connection is not None, "Failed to connect to the database"

    dump_file = dump(connection)
    assert dump_file is not None

    upload("test.sql", "test-bucket")

    assert True
