import click
import subprocess
from pathlib import Path
from string import capwords
from beaupy.spinners import *
from rich.console import Console
from beaupy import confirm, prompt, select
from tools.utils.tools_utils import ToolsUtils

console = Console()

dev_path = Path("./tools/tools-config.yaml")
prod_path = Path(".tools/tools-config.yaml")

utils = ToolsUtils(dev_path, prod_path)

# TODO: Refactor using Gum commands
@click.command("branch-new")
def cli():
	"""
	This command is used to create a new branch.
	"""
	config = utils.load_config()
	primary_color, secondary_color, _, _, prompt_color, cursor_style, cursor_color, _ = utils.load_theme(config)
	console.print("Creating a New Branch", style=primary_color, highlight=True)
	branch_prefixes = []
	for prefix in config['branches']['branch-prefixes']:
		branch_prefixes.append(f"[{secondary_color}]{prefix}[/{secondary_color}]")
	branch_type = select(
		options=branch_prefixes,
		cursor=cursor_style,
		cursor_style=cursor_color
		)
	branch_type = utils.remove_color_indicators(branch_type)
	has_corresponding_ticket = confirm(
		question=f"[{prompt_color}]Does this branch have a corresponding Linear ticket?[/{prompt_color}]",
		cursor=cursor_style,
		cursor_style=cursor_color
		)
	if has_corresponding_ticket:
		ticket_number = prompt(f"[{prompt_color}]Enter the ticket number[/{prompt_color}]")
		ticket_number = utils.remove_color_indicators(ticket_number)
		branch_ticket_ref = f"{config['general']['team-tag']}-{ticket_number}"
	branch_name = prompt(f"[{prompt_color}]Enter the branch name[/{prompt_color}]")
	branch_name = utils.remove_color_indicators(branch_name)
	pull_default_branch_name = "git rev-parse --abbrev-ref origin/HEAD"
	default_branch_output = subprocess.run(pull_default_branch_name, shell=True, check=True, cwd=Path.cwd(), stdout=subprocess.PIPE, text=True)
	default_branch = default_branch_output.stdout.strip()
	default_branch = default_branch.replace("origin/", "")
	cmd1 = f"git checkout {default_branch} && git pull"
	if has_corresponding_ticket:
		cmd2 = f"git checkout -b {branch_type}/{branch_ticket_ref}-{branch_name} && git push --set-upstream origin {branch_type}/{branch_ticket_ref}-{branch_name}"
	else:
		cmd2 = f"git checkout -b {branch_type}/{branch_name} && git push --set-upstream origin {branch_type}/{branch_name}"
	spinner = Spinner(LOADING, f"	  Pulling Down From {capwords(default_branch)}")
	spinner.start()
	subprocess.run(cmd1, shell=True, check=True, cwd=Path.cwd(), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
	subprocess.run(cmd2, shell=True, check=True, cwd=Path.cwd(), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
	spinner.stop()