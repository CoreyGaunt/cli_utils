import click
import subprocess
from pathlib import Path
from rich.console import Console
from tools.utils.tools_utils import ToolsUtils

console = Console()
utils = ToolsUtils()

@click.command("compare-objects")
def cli():
	"""
	Compare the objects in the current schema with the objects in the production schema.

	The interactive prompt will ask you to select a schema and a model to compare. The models shown are dependent on the schema you select.

	Once you've selected a model, you will be asked for the primary key of the model. This is used to compare the objects in the schema with the production schema.

	After the command is run, it will output the differences between the two objects as a sql query. Upon completion, the generated bash command will be added to your zsh history.
	"""
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