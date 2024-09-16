import re
import os
import click
import subprocess
from pathlib import Path
from rich.console import Console
from tools.utils.tools_utils import ToolsUtils

console = Console()
utils = ToolsUtils()

@click.command("run")
@click.option('--prod', '-p', is_flag=True, help="Run the dbt Models in the production environment.")
@click.option('--upstream', '-u', default='', is_flag=False, flag_value='+', help="Run the specified model & its parent models. You can also specify the number of levels to go up. E.g. 1+<model_name> or 2+<model_name>. Defaults to +<model_name>.")
@click.option('--downstream', '-d', default='', is_flag=False, flag_value='+', help="Run specified model & its children models. You can also specify the number of levels to go up. E.g. <model_name>+1 or <model_name>+2. Defaults to <model_name>+.")
@click.option('--waterfall', '-a', is_flag=True, help="Run the specified model, its children models, and the parents of its children models. Leverages the '@' dbt operator. NOTE - This command cannot be run alongside --upstream or --downstream.")
def cli(
	prod,
	upstream,
	downstream,
	waterfall
):
	"""
	Run dbt models in the local environment, or the production environment if the --prod flag is set.

	Production access is granted by Analytics Engineering. Please reach out to the team if you need access.

	This command will scan the models directory for .sql files and prompt you to select a model to run. You can also specify the number of upstream or downstream models to run alongside the selected model. If the --waterfall flag is set, it will run the selected model, its children models, and the parents of its children models.

	When the command completes (whether successful or not), it will add the generated bash command to your zsh history.
	"""
	config = utils.load_config()
	prefix, suffix = '', ''

	if waterfall:
		if upstream or downstream:
			console.print("Cannot run --waterfall with --upstream or --downstream", style="bold red")
			exit()
		prefix = '@'
	else:
		if upstream:
			if upstream == '+':
				prefix = upstream
			# Only accept int values ranging from 1 to 9
			else:
				if re.match(r'^[1-9]{1}$', upstream):
					prefix = f'{upstream}+'
				else:
					console.print("Invalid prefix. Please specify a number between 1 and 9", style="bold red")
					exit()
		if downstream:
			if downstream == '+':
				suffix = downstream
			# Only accept int values ranging from 1 to 9
			else:
				if re.match(r'^[1-9]{1}$', downstream):
					suffix = f'+{downstream}'
				else:
					console.print("Invalid prefix. Please specify a number between 1 and 9", style="bold red")
					exit()
	# Anchor to the target directory models/
	# Recursively list all .sql files in the target directory
	# Format each file to only show the basename and trim the file extension
	model_list = utils.find_all_files_in_directory('zsh', 'dbt/models/', 'sql')
	model_name = utils.gum_filter(model_list, "Select A Model To Run")
	model_string = f"{prefix}{model_name}{suffix}"

	if prod:
		prod_password = os.environ.get("LP_PRODUCTION_KEY")
		if not prod_password:
			console.print("Access Denied to Run Production Locally", style="bold red")
			exit()
		cmd = f"dbt run -s {model_string} --target prod"
	else:
		cmd = f"dbt run -s {model_string}"
	try:
		subprocess.run(cmd, shell=True, check=True, cwd=Path.cwd(), text=True)
		utils.add_cmd_to_zsh_history(cmd)
	except subprocess.CalledProcessError:
		console.print("An error occurred while running the dbt models", style="bold red")
		utils.add_cmd_to_zsh_history(cmd)
		exit()