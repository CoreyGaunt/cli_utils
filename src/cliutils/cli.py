from pathlib import Path
import click # type: ignore
from cliutils.cliutils_config import init_cliutils
from cliutils.tools.cliutils_tools import CLIUtils
from cliutils.commands import COMMANDS

config_path = Path.home() / ".cliutils" / "cliutils-config.yaml"

if not config_path.exists():
    init_cliutils()

utils = CLIUtils()
config = utils.load_config()

@click.group()
def cli():
    """
	This is a command line tool that helps with common git and python tasks.
	"""

for command in COMMANDS:
    cli.add_command(command)

if __name__ == "__main__":
    cli()
