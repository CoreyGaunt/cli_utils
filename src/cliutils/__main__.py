from pathlib import Path
import click # type: ignore
from cliutils.cliutils_config import init_cliutils
from cliutils.commands import COMMANDS

config_path = Path.home() / ".cliutils" / "cliutils-config.yaml"

if not config_path.exists():
    init_cliutils()

@click.group()
def main():
    """
	This is a command line tool that helps with common git and python tasks.
	"""

for command in COMMANDS:
    main.add_command(command)

if __name__ == "__main__":
    main()
