import sys
import click
import importlib
from pathlib import Path
from tools.utils.tools_utils import ToolsUtils



dev_path = Path("./tools/tools-config.yaml")
prod_path = Path(".tools/tools-config.yaml")

utils = ToolsUtils(dev_path, prod_path)

config = utils.load_config()
excluded_commands = [x for x in config['excluded-commands']]
commands_dir = Path.cwd() / "tools" / "commands"
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