from backup.s3 import (
    S3Config,
    _download,
    _upload,
)
from backup.options import (
    dir_options,
)
import click
from pathlib import Path


# S3 Flags
def s3_options(fn):
    options = [
        click.option(
            "--endpoint",
            "-e",
            show_default=True,
            help="S3 endpoint URL",
        ),
        click.option("--bucket", "-b", required=True, help="S3 bucket name"),
        click.option(
            "--key", "-k", envvar="ACCESS_KEY", help="S3 access key ID ($ACCESS_KEY)"
        ),
        click.option(
            "--secret",
            "-s",
            envvar="SECRET_KEY",
            help="S3 secret access key ($SECRET_KEY)",
        ),
    ]
    for option in options:
        fn = option(fn)
    return fn


@click.group()
def s3():
    """Commands for S3."""
    pass


@s3.command()
@s3_options
def ls(endpoint: str, bucket: str, key: str, secret: str):
    # TODO: Implement
    pass


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
