import click
import subprocess
from pathlib import Path
from rich.console import Console
from tools.utils.tools_utils import ToolsUtils

console = Console()
utils = ToolsUtils()

@click.command("reset-schemas")
@click.option('--ci-cd', '-ci', is_flag=True, help="Reset the schemas in the CI/CD environment.")
def cli(ci_cd):
	"""
	Reset the schemas in the local environment, or the CI/CD environment if the --ci-cd flag is set.

	This command will drop all of your current schemas, and copy production into your target environment.
	"""
	config = utils.load_config()
	primary_color, _, _, _, _, _, _, _ = utils.load_theme(config)
	if ci_cd:
		environment = "CI/CD"
		console.print("Resetting schemas in the CI/CD environment...", style=f"bold {primary_color}")
		cmd = "dbt run-operation prod_to_ci_cd_copy_schemas --target prod && dbt run -s config.materialized:view --target github"
	else:
		environment = "Local"
		console.print("Resetting schemas in the local environment...", style=f"bold {primary_color}")
		cmd = " dbt run-operation local_prod_copy_schemas && dbt run -s config.materialized:view"
	confirm_reset = utils.gum_confirm(f"Are you sure you want to reset the schemas in the {environment} environment?")
	if not confirm_reset:
		console.print("Reset operation aborted!!", style="bold red")
		exit()
	reset_outcome = subprocess.run(cmd, shell=True, check=True, cwd=Path.cwd(), text=True)
	if reset_outcome.returncode == 0:
		console.print("Schemas reset successfully!", style=f"bold {primary_color}")
	else:
		console.print("Error resetting schemas", style="bold red")
		utils.add_cmd_to_zsh_history(cmd)
