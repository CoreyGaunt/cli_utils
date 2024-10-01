import click
import subprocess
from pathlib import Path
from rich.console import Console
from tools.utils.tools_utils import ToolsUtils

console = Console()
utils = ToolsUtils()

@click.command("s3-sync")
def cli():
	"""
	This command is used to sync the local data with the S3 bucket.
	"""
	config = utils.load_config()
	primary_color, _, _, _, _, _, _, _ = utils.load_theme(config)
	console.print("Syncing Local Data With S3 Bucket", style=primary_color, highlight=True)
	gum_src_list = ""
	sources_options = [
		f"{config['aws-info']['dag-root']}",
		f"{config['aws-info']['plugins-root']}",
	]
	for source in sources_options:
		gum_src_list += f"'{source}' "

	src = utils.gum_choose(gum_src_list)
	if src == config['aws-info']['dag-root']:
		target = config['aws-info']['s3-dag-location']
	elif src == config['aws-info']['plugins-root']:
		target = config['aws-info']['s3-plugins-location']

	gum_confirm_output = utils.gum_confirm(f"Are you sure you want to sync {src.upper()} with {target.upper()}?")
	confirmation = gum_confirm_output

	if confirmation:
		cmd = f"aws s3 sync {src} {target} --exclude '**/.DS_Store' --exclude '**/__pycache__/**' --exclude '.DS_Store'"
		subprocess.run(cmd, shell=True, check=True, cwd=Path.cwd())
	else:
		console.print("Sync Cancelled", style="bold red")