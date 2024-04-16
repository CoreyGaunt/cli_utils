import click
import subprocess
from pathlib import Path
from tools.utils.tools_utils import ToolsUtils

utils = ToolsUtils()

@click.command("pr-create")
@click.option('--is-cross-team', '-c', is_flag=True, help="Create a cross-team pull request.")
def cli(is_cross_team):
	config = utils.load_config()
	pr_prefix = ""
	for prefix in config['branches']['branch-prefixes']:
		pr_prefix += f"'{prefix}' "
	pr_type = utils.gum_filter(pr_prefix, "What Type Of Pull Request Is This?")
	pr_title = utils.gum_input("What Do You Want To Name This PR?")
	template_dir_string = 'pull_request_templates'
	template_dir = list(Path.cwd().glob(f'**/{template_dir_string}'))[0]
	if is_cross_team:
		template = "cross_team_template.md"
	else:
		template = "data_science_and_analytics_template.md"
	template_file = template_dir / template
	pr_body_from_env = template_file.read_text()
	pr_body = utils.gum_write("What Did You Do?", pr_body_from_env)
	# handle special characters in pr_body that would cause in error
	cmd1 = f"gh pr create --title '[{pr_type.upper()}] - {pr_title}' --body '{pr_body}' --draft"
	subprocess.run(cmd1, shell=True, cwd=Path.cwd())