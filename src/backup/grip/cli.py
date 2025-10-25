from backup.grip import (
    GripConfig,
    _getGraphs,
    _getEdges,
    _getVertices,
    _dump as _gripDump,
    _restore as _gripRestore,
)
from backup.options import (
    dir_flags,
)
from pathlib import Path
import click
import logging
import json


# GRIP Flags
def grip_host_flags(fn):
    options = [
        click.option(
            "--host",
            "-H",
            envvar="GRIP_HOST",
            default="localhost",
            show_default=True,
            help="GRIP host ($GRIPHOST)",
        ),
        click.option(
            "--port",
            "-p",
            envvar="GRIP_PORT",
            default=8201,
            show_default=True,
            help="GRIP port ($GRIP_PORT)",
        ),
    ]
    for option in reversed(options):
        fn = option(fn)
    return fn

# GRIP Graph Flags
def grip_flags(fn):
    options = [
        click.option("--graph", "-g", default="CALYPR", help="Name of the GRIP graph."), 
        # click.option(
        #     "--edge",
        #     "--edges",
        #     "-e",
        #     is_flag=True,
        #     default=False,
        #     help="Output GRIP edges.",
        # ),
        # click.option("--graph", "-g", default="CALYPR", help="Name of the GRIP graph."),
        # click.option(
        #     "--vertex",
        #     "--vertices",
        #     "-v",
        #     is_flag=True,
        #     default=False,
        #     help="Output GRIP vertices.",
        # ),
    ]
    for option in reversed(options):
        fn = option(fn)
    return fn


@click.group()
def grip():
    """Commands for GRIP backups."""
    pass


@grip.command()
@grip_host_flags
def ls(host: str, port: int):
    """list GRIP vertices and/or edges"""
    conf = GripConfig(host=host, port=port)

    for v in _getGraphs(conf):
        click.echo(json.dumps(v, indent=2))


@grip.command()
@grip_host_flags
@dir_flags
def backup(host: str, port: int, graph: str, vertex: bool, edge: bool, dir: Path):
    """grip ➜ local"""
    conf = GripConfig(host=host, port=port)

    # Set timestamp
    dir.mkdir(parents=True, exist_ok=True)

    logging.debug(f"Backing up GRIP graph '{graph}' to directory '{dir}'")
    _gripDump(conf, graph, vertex, edge, dir)

    # TODO: Better way to handle GRIP graph schemas?
    schema = f"{graph}__schema__"
    logging.debug(f"Backing up GRIP graph '{schema}' to directory '{dir}'")
    _gripDump(conf, schema, vertex, edge, dir)


@grip.command()
@grip_host_flags
@grip_flags
@dir_flags
def restore(host: str, port: int, graph: str, dir: Path):
    """local ➜ grip"""
    conf = GripConfig(host=host, port=port)

    _ = _gripRestore(conf, graph, dir)
