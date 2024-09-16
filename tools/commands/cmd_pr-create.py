import click
import subprocess
import pkg_resources
from pathlib import Path
from tools.utils.tools_utils import ToolsUtils

utils = ToolsUtils()

@click.command("pr-create")
@click.option('--is-cross-team', '-c', is_flag=True, help="Create a cross-team pull request.")
def cli(is_cross_team):
	"""
	Opens a new draft pull request in the current repository.

	This command uses interactive prompting to generate a pull request title and body. The type of pull request is determined by the user's home .tools/tools-config.yaml file.
	The user is prompted to select a type of pull request from the available options. The title of the pull request is then generated by the user. The body of the pull request is generated from a template file, which is stored in the tools package.
	"""
	config = utils.load_config()
	# pr_prefix = ""
	# for prefix in config['branches']['branch-prefixes']:
	# 	pr_prefix += f"'{prefix}' "
	# pr_type = utils.gum_filter(pr_prefix, "What Type Of Pull Request Is This?")
	pr_ticket_confirm = utils.gum_confirm("Does this pull request have a corresponding ticket?")
	ticket_confirmation = pr_ticket_confirm
	if ticket_confirmation:
		pr_ticket = utils.gum_input("What Is The Ticket Number?")
		pr_ticket_reference = f"{config['general']['team-tag']}-{pr_ticket}"
		pr_header = f"{pr_ticket_reference}: "
	else:
		pr_header = ""
	pr_title = utils.gum_input("What Do You Want To Name This PR?")
	commands_dir = Path(pkg_resources.resource_filename(__name__, ''))
	template_dir = commands_dir.parent / "pull_request_templates"

	if is_cross_team:
		template = "cross_team_template.md"
	else:
		template = "data_dbt.md"
	template_file = template_dir / template
	pr_body_from_env = template_file.read_text()
	# Parse template file and look for 'replace_ticket_ref' and replace with pr_ticket_reference
	if pr_body_from_env.find("replace_ticket_ref") != -1:
		pr_body_from_env = pr_body_from_env.replace("replace_ticket_ref", pr_ticket_reference)
	pr_body = utils.gum_write("What Did You Do?", pr_body_from_env)
	# handle special characters in pr_body that would cause in error
	try:
		cmd1 = f"gh pr create --title '{pr_header}{pr_title}' --body $'{pr_body}' --draft"
		subprocess.run(cmd1, shell=True, cwd=Path.cwd(), check=True)
	except Exception as e:
		print("Attempting to create pull request without --draft flag")
		try:
			cmd2 = f"gh pr create --title '{pr_header}{pr_title}' --body $'{pr_body}'"
			subprocess.run(cmd2, shell=True, cwd=Path.cwd())
		except Exception as e:
			exit()