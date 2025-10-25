from backup.postgres import (
    PGConfig,
    _getDbs,
    _dump as _pgDump,
    _restore as _pgRestore,
)
from backup.options import (
    dir_flags,
)
import click
import logging
from pathlib import Path


# Postgres Flags
def pg_flags(fn):
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
    ]
    for option in reversed(options):
        fn = option(fn)
    return fn


@click.group()
def pg():
    """Postgres-related commands (moved from main.py)."""
    pass


@pg.command()
@pg_flags
def ls(host: str, port: int, user: str):
    """list databases"""
    conf = PGConfig(host=host, port=port, user=user)

    dbs = _getDbs(conf)
    if not dbs:
        logging.warning(f"No databases found at {conf.host}:{conf.port}.")
        return

    # List databases
    for database in dbs:
        click.echo(database)


@pg.command()
@pg_flags
@dir_flags
def dump(host: str, port: int, user: str, dir: Path):
    """postgres ➜ local"""
    conf = PGConfig(host=host, port=port, user=user)

    # Dump directory
    dir.mkdir(parents=True, exist_ok=True)

    dbs = _getDbs(conf)
    if not dbs:
        logging.warning(f"No databases found to dump at {conf.host}:{conf.port}.")
        return

    # Dump databases
    for database in dbs:
        dump = _pgDump(conf, database, dir)
        logging.debug(f"Dumped {database} to {dump}")


@pg.command()
@pg_flags
@dir_flags
def restore(host: str, port: int, user: str, dir: Path):
    """local ➜ postgres"""
    conf = PGConfig(host=host, port=port, user=user)

    dbs = _getDbs(conf)
    if not dbs:
        logging.warning(f"No databases found to restore at {conf.host}:{conf.port}.")
        return

    # Restore databases
    for database in dbs:
        _ = _pgRestore(conf, database, dir)
