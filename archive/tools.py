import os
import re
import yaml
import click
import shlex
import subprocess
import sqlparse
from sqlparse.tokens import Whitespace, Wildcard
from pathlib import Path
from typing import List
from string import capwords
from beaupy.spinners import *
from rich.console import Console
from beaupy import confirm, prompt, select, select_multiple, Config
from tools.utils.tools_utils import ToolsUtils

console = Console()

dev_path = Path("./tools/tools-config.yaml")
prod_path = Path(".tools/tools-config.yaml")
utils = ToolsUtils(dev_path, prod_path)

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
	Path(".tools").mkdir(exist_ok=True)
	# Check if Homebrew is installed, if not, install it

	team_tag = utils.gum_input("What is your team's Linear Tag?", "DSA")
	team_name = utils.gum_input("What is your team's name?", "Data Science & Analytics")
	with open(".tools/tools-config.yaml", "w") as file:
		file.write("general:\n")
		file.write(f'  team-tag: "{team_tag}"\n')
		file.write(f'  team-name: "{team_name}"\n')
		file.write("  raise-on-escape: true\n")
		file.write("  raise-on-interrupt: true\n")
		file.write("commits:\n")
		file.write("  conventional-commits:\n")
		file.write("	types:\n")
		file.write("	  - Feat\n")
		file.write("	  - Refactor\n")
		file.write("	  - Fix\n")
		file.write("	  - Docs\n")
		file.write("	  - Style\n")
		file.write("	  - Test\n")
		file.write("	  - Chore\n")
		file.write("aws-info:\n")
		file.write("  dag-root: ''\n")
		file.write("  plugins-root: ''\n")
		file.write("  s3-dag-location: ''\n")
		file.write("  s3-plugins-location: ''")
		file.write("theme:\n")
		file.write("  name: 'iron_gold'\n")
		file.write("excluded-commands:\n")
		file.write("  - cmd_s3_sync\n")
	console.print("Initialized .kit Directory", style="bold green")

@click.command("commit")
def commit():
	"""
	This command is used to commit all the changes in the current directory.
	It also asks for a commit message following the Conventional Commits standard.
	"""
	config = utils.load_config()
	gum_confirm_output = utils.gum_confirm("Do you want to commit all changes?")
	confirmation = gum_confirm_output

	if confirmation:
		commit_type, commit_message = utils.commit_type_and_message()
		cmd1 = "git add ."
		cmd2 = f"git commit -m '{commit_type}: {commit_message}'"
		cmd3 = "git push"
		subprocess.run(cmd1, shell=True, check=True, cwd=Path.cwd())
		subprocess.run(cmd2, shell=True, check=True, cwd=Path.cwd())
		subprocess.run(cmd3, shell=True, check=True, cwd=Path.cwd())
	else:
		# list all files that have been changed
		files = ""
		tracked_files_for_commit = ""
		changed_files = "git --no-optional-locks status --short"
		changed_files_output = subprocess.run(changed_files, shell=True, check=True, cwd=Path.cwd(), stdout=subprocess.PIPE, text=True)
		changed_files_list = changed_files_output.stdout.strip().split("\n")
		for file in changed_files_list:
			files += f"'{file.strip()}' "
		tracked_files = utils.gum_filter(files, "Which File(s) Would You Like To Add?", False)
		tracked_files = [file[2:] for file in tracked_files.split("\n") if file]
		for file in tracked_files:
			tracked_files_for_commit += f"{file} "
		cmd1 = f"git add {tracked_files_for_commit}"
		commit_type, commit_message = utils.commit_type_and_message()
		cmd2 = f"git commit -m '{commit_type}: {commit_message}'"
		cmd3 = "git push"
		subprocess.run(cmd1, shell=True, check=True, cwd=Path.cwd())
		subprocess.run(cmd2, shell=True, check=True, cwd=Path.cwd())
		subprocess.run(cmd3, shell=True, check=True, cwd=Path.cwd())

@click.command("s3-sync")
def dsa_s3_sync():
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

# TODO: Refactor using Gum commands
@click.command("branch-new")
def branch_new():
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

@click.command("pr-create")
@click.option('--is-cross-team', '-c', is_flag=True, help="Create a cross-team pull request.")
def pr_create(is_cross_team):
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

@click.command("run")
@click.option('--prod', '-p', is_flag=True, help="Run the dbt Models in the production environment.")
@click.option('--upstream', '-u', default='', is_flag=False, flag_value='+', help="Run the specified model & its parent models. You can also specify the number of levels to go up. E.g. 1+<model_name> or 2+<model_name>. Defaults to +<model_name>.")
@click.option('--downstream', '-d', default='', is_flag=False, flag_value='+', help="Run specified model & its children models. You can also specify the number of levels to go up. E.g. <model_name>+1 or <model_name>+2. Defaults to <model_name>+.")
@click.option('--waterfall', '-a', is_flag=True, help="Run the specified model, its children models, and the parents of its children models. Leverages the '@' dbt operator. NOTE - This command cannot be run alongside --upstream or --downstream.")
def dbt_run(prod, upstream, downstream, waterfall):
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
	model_list = utils.find_all_files_in_directory('zsh', 'models/', 'sql')
	model_name = utils.gum_filter(model_list, "Select A Model To Run")
	model_string = f"{prefix}{model_name}{suffix}"

	if prod:
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

@click.command("compare-objects")
def compare_objects():
	config = utils.load_config()
	schemas = "'utilities' 'sources' 'transform' 'dw'"
	mart_schemas_output = subprocess.run("find models/4_marts/ -type d -name 'mart_*' -exec basename {} \;", shell=True, check=True, stdout=subprocess.PIPE, text=True)
	mart_schemas = mart_schemas_output.stdout.strip().split("\n")
	for schema in mart_schemas:
		schemas += f" '{schema}'"
	schema = utils.gum_filter(schemas, "Select A Schema")
	if schema == "utilities":
		dir_location = "0_utilities"
	elif schema == "sources":
		dir_location = "1_sources"
	elif schema == "transform":
		dir_location = "2_transform"
	elif schema == "dw":
		dir_location = "3_dw"
	else:
		dir_location = f"4_marts/{schema}"
	# Anchor to the target directory models/
	# Recursively list all .sql files in the target directory
	# Format each file to only show the basename and trim the file extension
	model_list = ""
	models = subprocess.run(f"find models/{dir_location} -type f -name '*.sql' -exec basename {{}} .sql \;", shell=True, check=True, stdout=subprocess.PIPE, text=True)
	models = models.stdout.strip().split("\n")
	for model in models:
		model_list += f"'{model}' "
	model_name = utils.gum_filter(model_list, "Select A Model To Run")

	primary_key = utils.gum_input("What is the primary_key?")

	comparison_schema_output = subprocess.run("echo \"$DBT_SNOWFLAKE_TEST_SCHEMA\"", shell=True, check=True, stdout=subprocess.PIPE, text=True)
	comparison_schema = comparison_schema_output.stdout.strip().lower()

	cmd = f"dbt run-operation compare_objects --args \"{{comparison_schema : {comparison_schema}_{schema}, prod_schema : {schema}, object_name : {model_name}, primary_key: '{primary_key}'}}\""
	
	try:
		subprocess.run(cmd, shell=True, check=True, cwd=Path.cwd(), text=True)
		utils.add_cmd_to_zsh_history(cmd)
	except subprocess.CalledProcessError:
		console.print("An error occurred while running the dbt models", style="bold red")
		utils.add_cmd_to_zsh_history(cmd)
		exit()

@click.command("model-doc")
@click.option('--is-star-statement', '-ss', is_flag=True, help="Generate documentation for a model whose last statement is a 'SELECT *' statement.")
def model_doc(is_star_statement):
	config = utils.load_config()
	primary_color, secondary_color, tertiary_color, quaternary_color, prompt_color, cursor_style, cursor_color, filter_prompt = utils.load_theme(config)

	model_docs_location = Path('documentation/model_level/')
	model_docs = utils.find_all_files_in_directory('python', model_docs_location, 'md')
	model_docs = [x.split(".md")[0] for x in model_docs]

	column_docs_location = Path('documentation/column_level/')
	column_docs = utils.find_all_files_in_directory('python', column_docs_location, 'md')
	column_docs = [x.split(".md")[0] for x in column_docs]

	yaml_columns = []

	models = utils.find_all_files_in_directory('zsh', 'models/', 'sql')
	model_name = utils.gum_filter(models, "Select A Model To Document")
	# Check if a .yml file already exists for the selected model
	yml_search = subprocess.run(f"find models/ -type f -name '{model_name}.yml'", shell=True, check=True, stdout=subprocess.PIPE, text=True)
	if yml_search.stdout == "":
		console.print("No .yml file found for the selected model", style="bold green")
		console.print("Creating a new .yml file for the selected model", style="white")
		sql_file_path_base = subprocess.run(f"find models/ -type f -name '{model_name}.sql'", shell=True, check=True, stdout=subprocess.PIPE, text=True)
		sql_file_path = sql_file_path_base.stdout.strip().replace('models//', 'models/')
		console.print(f"Scanning model located at {sql_file_path.upper()} for yml generation", style=f"{primary_color}")
		# def scan_model_file(model_name):
		model_path = Path(sql_file_path)
		model_name = model_path.stem
		target_file = model_name + ".yml"
		destination_name = model_path.parent / target_file
		raw_sql = Path(model_path).read_text()
		raw_sql = re.sub(
			r"{{[A-Za-z\\n\s()=_,]+}}", "", raw_sql
		).strip()  # Strip out jinja config blocks
		raw_sql = re.sub(
			r"{{[A-Za-z_.()\[\]\',\s]+}}", "", raw_sql
		).strip() # Strip out jinja macro usage
		raw_sql = re.sub(r"\n+", "\n", raw_sql)  # Remove extra newlines
		parsed = sqlparse.parse(raw_sql)
		for statement in parsed:
			aliases = []
			final_cte = []
			cte_count = 0
			if statement.get_type() in ["SELECT", "UNKNOWN"]:
				non_whitespace_tokens = [x for x in statement.tokens if x.ttype is not Whitespace and x.ttype is not sqlparse.tokens.Newline]
				for i in range(len(non_whitespace_tokens)):
					if non_whitespace_tokens[i].ttype is sqlparse.tokens.Keyword.DML and non_whitespace_tokens[i].value.upper() == "SELECT":
						if (
							non_whitespace_tokens[i+1].ttype is sqlparse.tokens.Wildcard
							and type(non_whitespace_tokens[i-1]) is sqlparse.sql.Parenthesis
						):
							is_last_statement_a_star = True
						else:
							is_last_statement_a_star = False
				parenth_token_total = len([x for x in statement.tokens if type(x) is sqlparse.sql.Parenthesis])
				parenth_token_count = 0
				print(parenth_token_total)
				for token in statement.tokens:
					if token.ttype is None and type(token) is not sqlparse.sql.Function:
						if type(token) is sqlparse.sql.Identifier:
							if not token_is_cte(token):
								aliases.append(token.get_name())
							else:
								cte_count += 1
						elif type(token) is sqlparse.sql.IdentifierList:
							for child_token in token.get_identifiers():
								if (
									child_token.ttype is not sqlparse.tokens.Keyword
									and not token_is_cte(child_token)
									and child_token.get_name() is not None
								):
									child_token = check_for_real_name(child_token)
									if child_token[1]:
										new_name = child_token[0]
										try:
											new_name = child_token[0].split(".")[1]
										except:
											pass
										aliases.append(new_name)
						if type(token) is sqlparse.sql.Parenthesis:
							parenth_token_count += 1
							if parenth_token_count == parenth_token_total:
								parenth_key_staging = []
								for child_token in token.tokens:
									if not child_token.ttype is Whitespace:
										parenth_key_staging.append(child_token)
								for i in range(len(parenth_key_staging)):
									if (
										isinstance(parenth_key_staging[i], sqlparse.sql.Identifier)
										and parenth_key_staging[i-1].value != "from"
									):
										child_token = check_for_real_name(parenth_key_staging[i])
										if child_token[1]:
											new_name = child_token[0]
										try:
											new_name = child_token[0].split(".")[1]
										except:
											pass
										final_cte.append(new_name)
									elif parenth_key_staging[i].ttype is None and type(parenth_key_staging[i]) is sqlparse.sql.IdentifierList:
										for grandchild_token in parenth_key_staging[i].get_identifiers():
											column_name = check_for_real_name(grandchild_token)
											if column_name[1]:
												new_name = column_name[0]
											try:
												new_name = column_name[0].split(".")[1]
											except:
												pass
											final_cte.append(new_name)
		if is_last_statement_a_star == False:
			# returned_columns = aliases.pop()
			returned_columns = aliases
		else:
			returned_columns = final_cte

		column_docs = [x.split(".md")[0] for x in column_docs]

		for col in returned_columns:
			if col in column_docs:
				col_tuple = (col, True)
			else:
				col_tuple = (col, False)
			yaml_columns.append(col_tuple)

		model = {
			"version": 2,
			"models": [
				{
					"name": model_name,
					"description": "TODO: Add Description",
					"columns": generate_yaml_columns(yaml_columns),
				}
			],
		}

		destination_name.write_text(yaml.dump(model, sort_keys=False, default_flow_style=False))
	elif yml_search.stdout != "":
		console.print("A .yml file already exists for the selected model", style="bold red")
		exit()

def token_is_cte(token: sqlparse.sql.Token) -> bool:
    """Check if a given token is a CTE name so we can skip documenting it.

    Args:
        token (sqlparse.sql.Token): The token to check

    Returns:
        bool: True if the token is a CTE name, False otherwise
    """
    _, next_token = token.token_next(1)
    t_catch = "iff(" in token.value or "case " in token.value
    if t_catch:
        next_token = None
    return next_token and next_token.value == "as"

def check_for_real_name(token: sqlparse.sql.Token) -> sqlparse.sql.Token:
	t_value = token.value 
	t_value = re.sub(f"--.*", "", t_value)
	if " as " in t_value:
		real_name = t_value.split(" as ")[1]
		is_real = True
	elif (
		"()" in t_value
		or " " in t_value
	):
		real_name = t_value
		is_real = False
	else:
		real_name = t_value
		is_real = True

	return (real_name, is_real)

def generate_yaml_columns(yaml_columns):
	columns = []
	for column in yaml_columns:
		description = 'TODO: Add Description'
		if column[1]:
			description = f'{{{{ doc("{column[0]}") }}}}'
		column_dict = {
			"name": column[0],
			"description": description
		}
		columns.append(column_dict)
	
	return columns

cli.add_command(init)
cli.add_command(dsa_s3_sync)
cli.add_command(branch_new)
cli.add_command(commit)
cli.add_command(pr_create)
cli.add_command(dbt_run)
cli.add_command(compare_objects)
cli.add_command(model_doc)