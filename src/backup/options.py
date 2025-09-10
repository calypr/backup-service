from pathlib import Path
import click


# GRIP Flags
def grip_options(fn):
    options = [
        click.option(
            "--edge", "--edges", "-e", is_flag=True, help="Output GRIP edges."
        ),
        click.option("--graph", "-g", default="CALYPR", help="Name of the GRIP graph."),
        click.option(
            "--host",
            "-H",
            envvar="GRIP_HOST",
            default="localhost",
            show_default=True,
            help="GRIP host ($GRIPHOST)",
        ),
        click.option(
            "--limit",
            "-l",
            envvar="GRIP_LIMIT",
            type=int,
            default=10000,
            help="Limit number of items listed.",
        ),
        click.option(
            "--port",
            "-p",
            envvar="GRIP_PORT",
            default=8201,
            show_default=True,
            help="GRIP port ($GRIP_PORT)",
        ),
        click.option(
            "--vertex",
            "--vertices",
            "-v",
            is_flag=True,
            help="Output GRIP vertices.",
        ),

    ]
    for option in reversed(options):
        fn = option(fn)
    return fn


# Postgres Flags
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


# S3 Flags
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


# Output/intput directory flags
dir_options = click.option(
    "--dir",
    "-d",
    default=Path("."),
    type=click.Path(path_type=Path),
    show_default=True,
    help="Dump directory",
)
