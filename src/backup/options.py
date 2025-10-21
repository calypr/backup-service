from pathlib import Path
import click

# Common CLI Options for all subcommand

# Output/intput directory flags
dir_options = click.option(
    "--dir",
    "-d",
    default=Path("."),
    type=click.Path(path_type=Path),
    show_default=True,
    help="Dump directory",
)
