import click 
from pathlib import Path
from rich.console import Console
from ..utils.tools_utils import ToolsUtils

console = Console()

dev_path = Path("./tools/tools-config.yaml")
prod_path = Path(".tools/tools-config.yaml")

utils = ToolsUtils(dev_path, prod_path)

@click.command("init")
def cli():
	"""
	This command is used to create a .kit directory in the root of the project.
	Then it will create a kit_config.yaml file in the .kit directory.
	"""
	utils.check_and_install_terminal_requirements()
	# check if the .tools directory exists, and if the tools-config.yaml file exists
	confirmation = True
	if (
		Path(".tools").exists() and Path(".tools/tools-config.yaml").exists()
		or Path("./tools").exists() and Path("./tools/tools-config.yaml").exists()
	):
		confirmation = utils.gum_confirm("A .tools directory & tools-config.yaml file already exist. Do you want to overwrite them?")
	if confirmation:
		Path(".tools").mkdir(exist_ok=True)
		team_tag = utils.gum_input("What is your team's Linear Tag?", "DSA")
		team_name = utils.gum_input("What is your team's name?", "Data Science & Analytics")
		with open(".tools/tools-config.yaml", "w") as file:
			file.write("general:\n")
			file.write(f'  team-tag: "{team_tag}"\n')
			file.write(f'  team-name: "{team_name}"\n')
			file.write("  raise-on-escape: true\n")
			file.write("  raise-on-interrupt: true\n")
			file.write("commits:\n")
			file.write("  conventional-commits:\n")
			file.write("	types:\n")
			file.write("	  - Feat\n")
			file.write("	  - Refactor\n")
			file.write("	  - Fix\n")
			file.write("	  - Docs\n")
			file.write("	  - Style\n")
			file.write("	  - Test\n")
			file.write("	  - Chore\n")
			file.write("aws-info:\n")
			file.write("  dag-root: ''\n")
			file.write("  plugins-root: ''\n")
			file.write("  s3-dag-location: ''\n")
			file.write("  s3-plugins-location: ''")
			file.write("theme:\n")
			file.write("  name: 'iron_gold'\n")
			file.write("excluded-commands:\n")
			file.write("  - cmd_s3-sync\n")
			file.write("  - __init__\n")
		console.print("Initialized .tools Directory", style="bold green")
	else:
		console.print("Init Cancelled", style="bold red")