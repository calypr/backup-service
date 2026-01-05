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


def _getS3Client(s3: S3Config):
    """
    Returns a MinIO client configured with the provided S3 configuration.
    """
    
    # Remove 'https://' prefix if it exists
    s3.endpoint = s3.endpoint.removeprefix("https://")

    return Minio(
        f"{s3.endpoint}",
        credentials=EnvAWSProvider(),
        secure=True,
    )


def _upload(
    s3: S3Config,
    dir: Path,
):
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
        logging.error(f"{err}")
        return err


def _download(
    s3: S3Config,
    dir: Path,
):
    """
    Downloads a file from S3 (MinIO/Ceph compatible).
    """

    client = _getS3Client(s3)

    for obj in client.list_objects(s3.bucket, recursive=True):
        name = obj.object_name
        logging.debug(f"obj: {obj}")

        if name is None:
            continue

        path = (dir / name).as_posix()

        logging.debug(f"Downloading {name} from bucket {s3.bucket} to {path}")
        obj = client.fget_object(
            bucket_name=s3.bucket,
            object_name=name,
            file_path=path,
        )
