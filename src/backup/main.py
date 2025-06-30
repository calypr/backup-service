import click
from backup import (
    PostgresConfig,
    S3Config,
    _connect,
    _download,
    _dump,
    _dumpAll,
    _listDbs,
    _restore,
    _restoreAll,
    _upload,
)


@click.group()
@click.version_option()
def cli():
    pass


@cli.command()
@click.option(
    "--host", "-H", envvar="PGHOST", default="localhost", show_default=True, help="Postgres host ($PGHOST)"
)
@click.option(
    "--port", "-p", envvar="PGPORT", default=5432, show_default=True, help="Postgres port ($PGPORT)"
)
@click.option(
    "--user",
    "-u",
    envvar="PGUSER",
    default="postgres", show_default=True,
    help="Postgres username ($PGUSER)",
)
@click.option(
    "--password", "-P", envvar="PGPASSWORD", help="Postgres password ($PGPASSWORD)"
)
@click.option("--endpoint", "-e", required=True, help="S3 endpoint URL")
@click.option("--dir", "-d", required=False, default='.', show_default=True, help="Dump directory")
@click.option("--bucket", "-b", required=True, help="S3 bucket name")
@click.option("--key", "-k", required=True, help="S3 key id")
@click.option("--secret", "-s", required=True, help="S3 secret key")
def backup(host, port, user, password, endpoint, dir, bucket, key, secret):
    """Postgres ➜ S3"""
    p = PostgresConfig(host=host, port=port, user=user, password=password)
    s3 = S3Config(endpoint_url=endpoint, bucket=bucket, key=key, secret=secret)

    # Connect to Postgres
    c = _connect(p)
    
    # List databases 
    dbs = _listDbs(c)
    
    # Dump databases
    for db in dbs:
        _ = _dump(p, db, dir)
    
    # Upload dumps to S3
    err = _upload(s3, dir)
    if err:
        print(f"Error uploading to S3: {err}")
    else:
        print("Backup OK")


@cli.command()
@click.option(
    "--host", "-H", envvar="PGHOST", default="localhost", show_default=True, help="Postgres host ($PGHOST)"
)
@click.option(
    "--port", "-p", envvar="PGPORT", default=5432, show_default=True, help="Postgres port ($PGPORT)"
)
@click.option(
    "--user",
    "-u",
    envvar="PGUSER",
    default="postgres",
    show_default=True,
    help="Postgres username ($PGUSER)",
)
@click.option(
    "--password", "-P", envvar="PGPASSWORD", help="Postgres password ($PGPASSWORD)"
)
@click.option(
    "--dbs",
    "-d",
    multiple=True,
    help="Databases to dump (repeat for multiple, empty for all)",
)
@click.option("--output", "-o", default=".", show_default=True, help="Output directory for dumps")
def restore(host, port, user, password, dbs, dir):
    """S3 ➜ Postgres"""
    p = PostgresConfig(host=host, port=port, user=user, password=password)
    c = _connect(p)
    dir = _restore(p, dbs, dir)
    print(f"Dumped databases to {dir}")


@cli.command()
@click.option(
    "--host", "-H", envvar="PGHOST", default="localhost", show_default=True, help="Postgres host ($PGHOST)"
)
@click.option(
    "--port", "-p", envvar="PGPORT", default=5432, show_default=True, help="Postgres port ($PGPORT)"
)
@click.option(
    "--user",
    "-u",
    envvar="PGUSER",
    default="postgres",
    show_default=True,
    help="Postgres username ($PGUSER)",
)
@click.option(
    "--password", "-P", envvar="PGPASSWORD", help="Postgres password ($PGPASSWORD)"
)
@click.option(
    "--dbs",
    "-d",
    multiple=True,
    help="Databases to dump (repeat for multiple, empty for all)",
)
@click.option("--dir", "-d", default=".", show_default=True, help="Output directory for dumps")
def dump(host, port, user, password, dbs, dir):
    """Postgres ➜ local"""
    p = PostgresConfig(host=host, port=port, user=user, password=password)
    c = _connect(p)
    dbs = _listDbs(dbs) if dbs else _listDbs(c)
    for db in dbs:
        dump = _dump(p, db, dir)
        print(f"Dumped {db} to {dump}")


@cli.command(name="ls")
@click.option(
    "--host", "-H", envvar="PGHOST", default="localhost", show_default=True, help="Postgres host ($PGHOST)"
)
@click.option(
    "--port", "-p", envvar="PGPORT", default=5432, show_default=True, help="Postgres port ($PGPORT)"
)
@click.option(
    "--user",
    "-u",
    envvar="PGUSER",
    default="postgres", show_default=True,
    help="Postgres username ($PGUSER)",
)
@click.option(
    "--password", "-P", envvar="PGPASSWORD", help="Postgres password ($PGPASSWORD)"
)
def listDbs(host, port, user, password):
    """List databases"""
    p = PostgresConfig(host=host, port=port, user=user, password=password)
    c = _connect(p)
    dbs = _listDbs(c)
    for db in dbs:
        print(db)


@cli.command()
@click.option("--endpoint", "-e", required=True, help="S3 endpoint URL")
@click.option("--bucket", "-b", required=True, help="S3 bucket name")
@click.option("--key", "-k", required=True, help="S3 key id")
@click.option("--secret", "-s", required=True, help="S3 secret key")
@click.option("--dir", "-d", required=True, help="Dump directory")
def download(endpoint, bucket, key, secret, dir):
    """S3 ➜ local"""
    s3 = S3Config(endpoint_url=endpoint, bucket=bucket, key=key, secret=secret)
    err = _download(s3, dir)
    if err:
        print(f"Error uploading to S3: {err}")
    else:
        print("Upload OK")


@cli.command()
@click.option("--endpoint", "-e", required=True, help="S3 endpoint URL")
@click.option("--bucket", "-b", required=True, help="S3 bucket name")
@click.option("--key", "-k", required=True, help="S3 key id")
@click.option("--secret", "-s", required=True, help="S3 secret key")
@click.option("--dir", "-d", required=True, help="Dump directory")
def upload(endpoint, bucket, key, secret, dir):
    """local ➜ S3"""
    s3 = S3Config(endpoint_url=endpoint, bucket=bucket, key=key, secret=secret)
    err = _upload(s3, dir)
    if err:
        print(f"Error uploading to S3: {err}")
    else:
        print("Upload OK")


if __name__ == "__main__":
    cli()
