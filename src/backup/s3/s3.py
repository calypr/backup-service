from dataclasses import dataclass
import logging
from pathlib import Path
from minio import Minio
from minio.credentials.providers import EnvAWSProvider


@dataclass
class S3Config:
    """S3 config"""

    endpoint: str
    bucket: str
    key: str
    secret: str


def _getS3Client(s3: S3Config):
    """
    Returns a MinIO client configured with the provided S3 configuration.
    """
    return Minio(
        f"{s3.endpoint}",
        access_key=s3.key,
        secret_key=s3.secret,
        credentials=EnvAWSProvider(),
    )


def _upload(
    s3: S3Config,
    dir: Path,
) -> Exception | None:
    """
    Uploads a file to S3 (MinIO/Ceph compatible).
    """

    client = _getS3Client(s3)

    try:
        logging.debug(f"dir: {dir}, type: {type(dir)}")

        # TODO: Review if this selection/filter of files is acceptable
        for dump in dir.rglob("*"):

            # Skip directories and non-files
            if not dump.is_file():
                continue

            logging.debug(
                f"Uploading {dump} to {s3.endpoint}/{s3.bucket}/{dump.as_posix()}"
            )

            client.fput_object(
                bucket_name=s3.bucket,
                object_name=dump.as_posix(),
                file_path=dump.as_posix(),
            )

    except Exception as err:
        logging.error(f"Failed to upload files to S3: {err}")
        return err

    return None


def _download(
    s3: S3Config,
    dir: Path,
) -> Exception | None:
    """
    Downloads a file from S3 (MinIO/Ceph compatible).
    """

    client = _getS3Client(s3)

    try:
        for obj in client.list_objects(s3.bucket, recursive=True):
            name = obj.object_name
            logging.debug(f"obj: {obj}")

            if name is None:
                continue

            path = (dir / name).as_posix()

            logging.debug(f"Downloading {name} from bucket {s3.bucket} to {path}")
            _ = client.fget_object(
                bucket_name=s3.bucket,
                object_name=name,
                file_path=path,
            )

    except Exception as err:
        logging.error(f"Failed to download files from S3: {err}")
        return err

    return None
