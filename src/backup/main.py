import click
from backup import connect, dump, upload
import importlib.metadata


@click.command()
@click.option(
    "--host", "-H", envvar="PGHOST", required=True, help="Postgres host ($PGHOST)"
)
@click.option(
    "--database",
    "-d",
    envvar="PGDATABASE",
    required=True,
    help="Postgres database name ($PGDATABASE)",
)
@click.option(
    "--user", "-u", envvar="PGUSER", required=True, help="Postgres username ($PGUSER)"
)
@click.option(
    "--password",
    "-p",
    envvar="PGPASSWORD",
    help="Postgres password ($PGPASSWORD)",
    required=True,
)
@click.option(
    "--output",
    "-o",
    required=True,
    help="Output of database dump (e.g. s3://example-bucket/)",
)
@click.option("--verbose", "-v", is_flag=True, help="Enable verbose output.")
@click.version_option()
def cli(
    database: str,
    host: str,
    user: str,
    password: str,
    output: str,
    verbose: bool,
):
    if verbose:
        print("Verbose mode is enabled.")

    conn = connect(database, host, user, password)
    if not conn:
        print("Failed to connect to the database.")
        return

    dump_file = dump(conn)
    if not dump_file:
        print("Failed to create database dump.")
        return

    upload(dump_file, output)


if __name__ == "__main__":
    cli()
