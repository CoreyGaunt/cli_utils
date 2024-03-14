import yaml
import click
import subprocess
import contextlib
import io
import sys
from pathlib import Path
from beaupy import confirm, prompt, select, select_multiple, Config
from beaupy.spinners import *
from rich.console import Console

console = Console()

dev_path = Path("./cli_kit/kit_config.yaml")
prod_path = Path(".kit/kit_config.yaml")

@click.group()
def cli():
	"""
	This is a command line tool that helps with common git and python tasks.
	"""
	pass

@click.command("init")
def init():
	"""
	This command is used to create a .kit directory in the root of the project.
	Then it will create a kit_config.yaml file in the .kit directory.
	"""
	Path(".kit").mkdir(exist_ok=True)
	with open(".kit/kit_config.yaml", "w") as file:
		file.write("general:\n")
		file.write("  team-tag: \n")
		file.write("  team-name: \n")
		file.write("  raise-on-escape: true\n")
		file.write("  raise-on-interrupt: true\n")
		file.write("commits:\n")
		file.write("  conventional-commits:\n")
		file.write("    types:\n")
		file.write("      - Feat\n")
		file.write("      - Refactor\n")
		file.write("      - Fix\n")
		file.write("      - Docs\n")
		file.write("      - Style\n")
		file.write("      - Test\n")
		file.write("      - Chore\n")
		file.write("aws-info:\n")
		file.write("  local-dag-root: ''\n")
		file.write("  local-plugins-root: ''\n")
		file.write("  cd-dag-root: ''\n")
		file.write("  cd-plugins-root: ''\n")
		file.write("  dag-location: ''\n")
		file.write("  plugins-location: ''")
	console.print("Initialized .kit Directory", style="bold green")

def load_config():
	try:
		if dev_path.exists():
			file_location = dev_path
		elif prod_path.exists():
			file_location = prod_path
		else:
			raise FileNotFoundError
		with open(f"{file_location}") as stream:
			try:
				config = yaml.safe_load(stream)
				Config.raise_on_escape = config["general"]["raise-on-escape"]
				Config.raise_on_interrupt = config["general"]["raise-on-interrupt"]
			except yaml.YAMLError as exc:
				print(exc)
	except FileNotFoundError:
		console.print("No kit_config.yaml File Found", style="bold red")
		console.print("Run 'kit init' to create a kit_config.yaml file", style="cyan")
		exit()
	return config

@click.command("commit-all")
def commit_all():
	"""
	This command is used to commit all the changes in the current directory.
	It also asks for a commit message following the Conventional Commits standard.
	"""
	config = load_config()
	commit_scopes = []
	for scope in config["commits"]["conventional-commits"]["types"]:
		commit_scopes.append(f"[bold blue]{scope}[/bold blue]")

	console.print("Committing All Changes", style="bold purple", highlight=True)
	commit_type = select(
		options=commit_scopes,
		cursor=">>>",
		cursor_style="bold deep_pink3"
		)
	cmd1 = "git add ."
	cmd2 = f"git commit -m '{commit_type}: {prompt('[bold deep_pink3]Enter the commit message[/bold deep_pink3]')}'"
	cmd3 = "git push"
	subprocess.run(cmd1, shell=True, check=True, cwd=Path.cwd())
	subprocess.run(cmd2, shell=True, check=True, cwd=Path.cwd())
	subprocess.run(cmd3, shell=True, check=True, cwd=Path.cwd())

@click.command("dsa-s3-sync")
def dsa_s3_sync():
	"""
	This command is used to sync the local data with the S3 bucket.
	"""
	config = load_config()
	console.print("Syncing Local Data With S3 Bucket", style="bold purple")
	sources = [
		f"{config['aws-info']['cd-dag-root']}",
		f"{config['aws-info']['cd-plugins-root']}",
		f"{config['aws-info']['local-dag-root']}",
		f"{config['aws-info']['local-plugins-root']}"
	]
	targets = [
		f"{config['aws-info']['dag-location']}",
		f"{config['aws-info']['plugins-location']}"
	]
	source_selection = select(
		options=sources,
		cursor=">>>",
		cursor_style="bold blue"
		)
	target_selection = select(
		options=targets,
		cursor=">>>",
		cursor_style="bold blue"
		)
	confirmation = confirm(
		question=f"Are you sure you want to sync {source_selection} with {target_selection}?",
		yes_text="I am sure, sync it",
		no_text="Nope! Go back!",
		cursor=">>>",
		cursor_style="bold blue")
	if confirmation:
		cmd = f"aws s3 sync {source_selection} {target_selection} --exclude '**/.DS_Store' --exclude '**/__pycache__/**' --exclude '.DS_Store'"
		subprocess.run(cmd, shell=True, check=True, cwd=Path.cwd())
	else:
		console.print("Sync Cancelled", style="bold red")

@click.command("branch-new")
def branch_new():
	"""
	This command is used to create a new branch.
	"""
	config = load_config()
	branch_prefixes = []
	for prefix in config['branches']['branch-prefixes']:
		branch_prefixes.append(prefix)
	branch_type = select(branch_prefixes)
	has_corresponding_ticket = confirm("Does this work pertain to a Linear ticket?")
	if has_corresponding_ticket:
		ticket_number = prompt("Enter the ticket number")
		branch_ticket_ref = f"{config['general']['team-tag']}-{ticket_number}"
	branch_name = prompt("Enter the branch name")
	cmd1 = "git checkout main && git pull"
	if has_corresponding_ticket:
		cmd2 = f"git checkout -b {branch_type}/{branch_ticket_ref}-{branch_name} && git push --set-upstream origin {branch_type}/{branch_ticket_ref}-{branch_name}"
	else:
		cmd2 = f"git checkout -b {branch_type}/{branch_name} && git push --set-upstream origin {branch_type}/{branch_name}"
	spinner = Spinner(LOADING, "      Pulling Down From Main")
	spinner.start()
	subprocess.run(cmd1, shell=True, check=True, cwd=Path.cwd(), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
	subprocess.run(cmd2, shell=True, check=True, cwd=Path.cwd(), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
	spinner.stop()
	
	

cli.add_command(init)
cli.add_command(commit_all)
cli.add_command(dsa_s3_sync)
cli.add_command(branch_new)