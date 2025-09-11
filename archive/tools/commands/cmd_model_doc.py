import re
import yaml
import click
import sqlparse
import subprocess
from pathlib import Path
from rich.console import Console
from sqlparse.tokens import Whitespace
from tools.utils.tools_utils import ToolsUtils

console = Console()
utils = ToolsUtils()

@click.command("model-doc")
@click.option('--is-star-statement', '-ss', is_flag=True, help="Generate documentation for a model whose last statement is a 'SELECT *' statement.")
def cli(is_star_statement):
	"""
	IN DEVELOPMENT! Creates a .yml file for a selected model.

	This command will scan the selected model file for column names and generate a .yml file for the selected model. If a .yml file already exists for the selected model, it will notify you and exit.

	It currently works best for models that have a final select statement with unaliased columns without any transformations.
	"""
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
			if statement.get_type() in ["SELECT", "UNKNOWN"]:
				for token in statement.tokens:
					if token.ttype is None and type(token) is not sqlparse.sql.Function:
						if type(token) is sqlparse.sql.Identifier:
							if not token_is_cte(token):
								aliases.append(token)
							else:
								cte_count += 1
						elif type(token) is sqlparse.sql.IdentifierList:
							for child_token in token.get_identifiers():
								if (
									child_token.ttype is not sqlparse.tokens.Keyword
									and not token_is_cte(child_token)
									# and child_token.get_name() is not None
								):
									aliases.append(child_token)
						# if type(token) is sqlparse.sql.Parenthesis:
						# 	parenth_token_count += 1
						# 	if parenth_token_count == parenth_token_total:
						# 		parenth_key_staging = []
						# 		for child_token in token.tokens:
						# 			if not child_token.ttype is Whitespace:
						# 				parenth_key_staging.append(child_token)
						# 		for i in range(len(parenth_key_staging)):
						# 			if (
						# 				isinstance(parenth_key_staging[i], sqlparse.sql.Identifier)
						# 				and parenth_key_staging[i-1].value != "from"
						# 			):
						# 				child_token = check_for_real_name(parenth_key_staging[i])
						# 				if child_token[1]:
						# 					new_name = child_token[0]
						# 				try:
						# 					new_name = child_token[0].split(".")[1]
						# 				except:
						# 					pass
						# 				final_cte.append(new_name)
						# 			elif parenth_key_staging[i].ttype is None and type(parenth_key_staging[i]) is sqlparse.sql.IdentifierList:
						# 				for grandchild_token in parenth_key_staging[i].get_identifiers():
						# 					column_name = check_for_real_name(grandchild_token)
						# 					if column_name[1]:
						# 						new_name = column_name[0]
						# 					try:
						# 						new_name = column_name[0].split(".")[1]
						# 					except:
						# 						pass
						# 					final_cte.append(new_name)
			returned_columns = []
			for alias in aliases:
				returned_columns.append(alias.get_name())

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
    return next_token and next_token.value == "as"

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