from backup.s3 import (
    S3Config,
    _download,
    _upload,
)
from backup.options import (
    dir_options,
    s3_options,
)
import click
from pathlib import Path


@click.group()
def s3():
    """Commands for S3."""
    pass


@s3.command()
@s3_options
def ls(endpoint: str, bucket: str, key: str, secret: str):
    """list S3 bucket contents"""
    conf = S3Config(endpoint=endpoint, bucket=bucket, key=key, secret=secret)

    objects = _getObjects(conf)
    if not objects:
        click.echo(f"No objects found in bucket '{bucket}'.")
        return

    # List objects
    for obj in objects:
        click.echo(obj)


@s3.command()
@s3_options
@dir_options
def download(endpoint: str, bucket: str, key: str, secret: str, dir: Path):
    """s3 ➜ local"""
    conf = S3Config(endpoint=endpoint, bucket=bucket, key=key, secret=secret)

    # Download from S3
    _ = _download(conf, dir)


@s3.command()
@s3_options
@dir_options
def upload(endpoint: str, bucket: str, key: str, secret: str, dir: Path):
    """local ➜ s3"""
    s3 = S3Config(endpoint=endpoint, bucket=bucket, key=key, secret=secret)

    # Upload to S3
    _ = _upload(s3, dir)
