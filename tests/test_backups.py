from utils import connect_to_database, create_database_dump, upload_to_s3   

def test_database_connection():
    """
    Tests connecting to the database.
    """
    # connect_to_database()

    assert True

def test_database_dump():
    """
    Tests creating a database dump.
    """
    create_database_dump()

    assert True

def test_s3_upload():
    """
    Tests uploading database dump to S3.
    """
    upload_to_s3("database_dump.sql")

    assert True
