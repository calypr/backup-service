from utils import connect_to_database, create_database_dump, upload_to_s3

def main():
    print("Hello from backup-service!")

    connect_to_database()
    create_database_dump()
    upload_to_s3("database_dump.sql")

if __name__ == "__main__":
    main()
