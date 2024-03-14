import yaml
import click
import subprocess
from pathlib import Path
from beaupy import confirm, prompt, select, select_multiple, Config
from rich.console import Console

with open("kit_config.yaml") as stream:
	try:
		config = yaml.safe_load(stream)
	except yaml.YAMLError as exc:
		print(exc)

Config.raise_on_escape = config["general"]["raise-on-escape"]
Config.raise_on_interrupt = config["general"]["raise-on-interrupt"]

console = Console()

@click.group()
def cli():
	"""
	This is a command line tool that helps with common git and python tasks.
	"""
	pass

@click.command("commit-all")
def commit_all():
	"""
	This command is used to commit all the changes in the current directory.
	It also asks for a commit message following the Conventional Commits standard.
	"""
	commit_scopes = []
	for scope in config["commits"]["conventional-commits"]["types"]:
		commit_scopes.append(scope)

	console.print("Committing All Changes", style="bold green")
	commit_type = select(commit_scopes)
	cmd1 = "git add ."
	cmd2 = f"git commit -m '{commit_type}: {prompt('Enter the commit message')}'"
	cmd3 = "git push"
	subprocess.run(cmd1, shell=True, check=True, cwd=Path.cwd())
	subprocess.run(cmd2, shell=True, check=True, cwd=Path.cwd())
	subprocess.run(cmd3, shell=True, check=True, cwd=Path.cwd())

@click.command("dsa-s3-sync")
def dsa_s3_sync():
	"""
	This command is used to sync the local data with the S3 bucket.
	"""
	console.print("Syncing Local Data With S3 Bucket", style="bold green")
	sources = [
		f"{config['aws-info']['cd_dag_root']}",
		f"{config['aws-info']['cd_plugins_root']}"
	]
	targets = [
		f"{config['aws-info']['dag-location']}",
		f"{config['aws-info']['plugins-location']}"
	]
	source_selection = select(sources)
	target_selection = select(targets)
	confirmation = confirm(f"Are you sure you want to sync {source_selection} with {target_selection}?")
	if confirmation:
		cmd = f"aws s3 sync {source_selection} {target_selection} --exclude '**/.DS_Store' --exclude '**/__pycache__/**' --exclude '.DS_Store'"
		subprocess.run(cmd, shell=True, check=True, cwd=Path.cwd())
	else:
		console.print("Sync Cancelled", style="bold red")

cli.add_command(commit_all)
cli.add_command(dsa_s3_sync)