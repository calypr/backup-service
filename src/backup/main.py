from backup import (
    connect,
    dumpDbs,
    listDbs,
    upload,
    PostgresConfig,
    S3Config,
)

import click


@click.command()

# Postgres Config
@click.option(
    "--host",
    "-H",
    envvar="PGHOST",
    help="Postgres host ($PGHOST)",
    default="localhost",
)
@click.option(
    "--port",
    "-p",
    envvar="PGPORT",
    help="Postgres port ($PGPORT)",
    default=5432,
)
@click.option(
    "--user",
    "-u",
    envvar="PGUSER",
    help="Postgres username ($PGUSER)",
    default="postgres",
)
@click.option(
    "--password",
    "-P",
    envvar="PGPASSWORD",
    help="Postgres password ($PGPASSWORD)",
)

# S3 Config
@click.option(
    "--endpoint",
    "-e",
    help="S3 endpoint URL (e.g. rgw.ohsu.edu)",
    required=True,
)
@click.option(
    "--bucket",
    "-b",
    help="S3 bucket name (e.g. example-bucket)",
)
@click.option(
    "--key",
    "-k",
    help="S3 key id",
)
@click.option(
    "--secret",
    "-s",
    help="S3 secret key",
)
@click.version_option()
def cli(
    host: str,
    port: int,
    user: str,
    password: str,
    endpoint: str,
    bucket: str,
    key: str,
    secret: str,
):
    # Postgres config
    p = PostgresConfig(
        host=host,
        port=port,
        user=user,
        password=password,
    )

    # S3 config
    s3 = S3Config(
        endpoint_url=endpoint,
        bucket=bucket,
        key=key,
        secret=secret,
    )

    # 1. Connect to Postgres
    c = connect(p)

    # 2. List databases
    dbs = listDbs(c)

    # 3. Dump databases
    dir = dumpDbs(p, dbs)

    # 4. Upload dump to S3
    err = upload(s3, dir)

    if err:
        print(f"Error uploading to S3: {err}")
    else:
        print("OK")

if __name__ == "__main__":
    cli()
