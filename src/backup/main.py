from click_aliases import ClickAliasedGroup
from elasticsearch.exceptions import ElasticsearchWarning
import click
import logging
import warnings

# Import command groups from subpackages
from .elasticsearch.cli import es as es_command
from .grip.cli import grip as grip_command
from .postgres.cli import pg as pg_command
from .s3.cli import s3 as s3_command


@click.group(cls=ClickAliasedGroup)
@click.version_option()
@click.option(
    "--verbose",
    "-v",
    "--debug",
    is_flag=True,
    default=False,
    help="Enable debug logging.",
)
def cli(verbose: bool):
    # Set default logging level
    level = logging.WARNING

    # Set verbose logging level
    if verbose:
        level = logging.DEBUG

    logging.basicConfig(
        level=level,
        format="%(asctime)s - %(levelname)s - %(message)s",
    )

    # Avoid INFO and ElasticsearchWarning logging from the elasticsearch logger
    # ref: https://stackoverflow.com/a/47157553
    logging.getLogger("elastic_transport.transport").setLevel(logging.CRITICAL)
    warnings.simplefilter("ignore", ElasticsearchWarning)


# register subcommands
cli.add_command(es_command)
cli.add_command(grip_command)
cli.add_command(pg_command)
cli.add_command(s3_command)

if __name__ == "__main__":
    cli()
