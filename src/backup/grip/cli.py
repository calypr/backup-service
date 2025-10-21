from backup.grip import (
    GripConfig,
    _getEdges,
    _getVertices,
    _dump as _gripDump,
    _restore as _gripRestore,
)
from backup.options import (
    dir_options,
    grip_options,
)
from pathlib import Path
import click
import logging
import json


@click.group()
def grip():
    """Commands for GRIP backups."""
    pass


@grip.command()
@grip_options
def ls(host: str, port: int, graph: str, vertex: bool, edge: bool):
    """list GRIP vertices and/or edges"""
    conf = GripConfig(host=host, port=port)

    if vertex:
        logging.debug(
            f"Listing vertices from GRIP graph '{graph}' at {conf.host}:{conf.port}"
        )
        for v in _getVertices(conf, graph):
            click.echo(json.dumps(v, indent=2))

    if edge:
        logging.debug(
            f"Listing edges from GRIP graph '{graph}' at {conf.host}:{conf.port}"
        )
        for e in _getEdges(conf, graph):
            click.echo(json.dumps(e, indent=2))


@grip.command()
@grip_options
@dir_options
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
@grip_options
@dir_options
def restore(host: str, port: int, graph: str, vertex: bool, edge: bool, dir: Path):
    """local ➜ grip"""
    conf = GripConfig(host=host, port=port)

    _ = _gripRestore(conf, graph, dir)
