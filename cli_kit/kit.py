import yaml
import click
import subprocess
from pathlib import Path
from beaupy import confirm, prompt, select, select_multiple
from rich.console import Console

with open("kit_config.yaml") as stream:
	try:
		config = yaml.safe_load(stream)
	except yaml.YAMLError as exc:
		print(exc)

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

cli.add_command(commit_all)