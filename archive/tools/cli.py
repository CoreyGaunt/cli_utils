import sys
import click
import importlib
import importlib.util
from importlib import resources
from pathlib import Path
from tools.tools_config import init_tools
from tools.utils.tools_utils import ToolsUtils

config_path = Path.home() / ".tools" / "tools-config.yaml"

if not config_path.exists():
	init_tools()

utils = ToolsUtils()

config = utils.load_config()

excluded_commands = [x for x in config['excluded-commands']]
tools_dir = Path(__file__).parent
commands_dir = tools_dir / "commands"
commands = [x.stem for x in commands_dir.glob("*.py") if x.stem not in excluded_commands]
command_names = [x[4:] for x in commands]

@click.group()
def cli():
	"""
	This is a command line tool that helps with common git and python tasks.
	"""
    
	pass

# Import commands from the list of py files in commands
for command in commands:
    try:
        spec = importlib.util.spec_from_file_location(f"tools.commands.{command}", commands_dir / f"{command}.py")
        mod = importlib.util.module_from_spec(spec)
        sys.modules[spec.name] = mod 
        spec.loader.exec_module(mod)
        cli.add_command(mod.cli)
    except Exception as e:
        print(f"Error importing {command}: {e}")

if __name__ == "__main__":
	cli()
