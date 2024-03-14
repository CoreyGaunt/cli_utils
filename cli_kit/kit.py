import yaml
import click
import subprocess
from pathlib import Path
from beaupy import confirm, prompt, select, select_multiple, Config
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

cli.add_command(init)

def load_config():
	try:
		if dev_path.exists():
			file_location = dev_path
		elif prod_path.exists():
			print("Found")
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
	config = load_config()
	console.print("Syncing Local Data With S3 Bucket", style="bold green")
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