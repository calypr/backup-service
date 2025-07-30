from pathlib import Path
import click


def es_options(fn):
    options = [
        click.option(
            "--host",
            "-H",
            envvar="ES_HOST",
            default="localhost",
            show_default=True,
            help="ElasticSearch host ($ES_HOST)",
        ),
        click.option(
            "--port",
            "-p",
            envvar="ES_PORT",
            default=9200,
            show_default=True,
            help="ElasticSearch port ($ES_PORT)",
        ),
        click.option(
            "--user",
            "-u",
            envvar="ES_USER",
            default="elastic",
            show_default=True,
            help="ElasticSearch username ($ES_USER)",
        ),
        click.option(
            "--password",
            "-P",
            envvar="ES_PASSWORD",
            help="ElasticSearch password ($ES_PASSWORD)",
        ),
        # click.option(
        #     "--repo",
        #     "-r",
        #     envvar="ES_REPO",
        #     default="backup_repo",
        #     show_default=True,
        #     help="ElasticSearch snapshot repository name ($ES_REPO)",
        # ),
        # click.option(
        #     "--bucket",
        #     "-b",
        #     envvar="ES_BUCKET",
        #     default="backup_bucket",
        #     show_default=True,
        #     help="S3 bucket name for ElasticSearch backups ($ES_BUCKET)",
        # ),
        # click.option(
        #     "--endpoint",
        #     "-e",
        #     envvar="ES_ENDPOINT",
        #     default="https://s3.amazonaws.com",
        #     show_default=True,
        #     help="S3 endpoint URL for ElasticSearch backups ($ES_ENDPOINT)",
        # ),
    ]
    for option in reversed(options):
        fn = option(fn)
    return fn


def pg_options(fn):
    options = [
        click.option(
            "--host",
            "-H",
            envvar="PGHOST",
            default="localhost",
            show_default=True,
            help="Postgres host ($PGHOST)",
        ),
        click.option(
            "--port",
            "-p",
            envvar="PGPORT",
            default=5432,
            show_default=True,
            help="Postgres port ($PGPORT)",
        ),
        click.option(
            "--user",
            "-u",
            envvar="PGUSER",
            default="postgres",
            show_default=True,
            help="Postgres username ($PGUSER)",
        ),
        click.option(
            "--password",
            "-P",
            envvar="PGPASSWORD",
            help="Postgres password ($PGPASSWORD)",
        ),
    ]
    for option in reversed(options):
        fn = option(fn)
    return fn


def s3_options(fn):
    options = [
        click.option(
            "--endpoint",
            "-e",
            default="https://s3.amazonaws.com",
            show_default=True,
            help="S3 endpoint URL",
        ),
        click.option("--bucket", "-b", required=True, help="S3 bucket name"),
        # TODO: Support env variables for S3 credentials
        # ref: https://github.com/minio/minio-go/blob/v7.0.95/pkg/credentials/env_aws.go#L27-L28
        click.option("--key", "-k", help="S3 access key ID ($AWS_ACCESS_KEY)"),
        click.option("--secret", "-s", help="S3 secret access key ($AWS_SECRET_KEY)"),
    ]
    for option in options:
        fn = option(fn)
    return fn


dir_options = click.option(
    "--dir",
    "-d",
    default=Path("."),
    type=click.Path(path_type=Path),
    show_default=True,
    help="Dump directory",
)
