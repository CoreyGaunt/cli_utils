import re
import yaml
import click
import sqlparse
import subprocess
from pathlib import Path
from rich.console import Console
from sqlparse.tokens import Whitespace
from ..utils.tools_utils import ToolsUtils

console = Console()

dev_path = Path("./tools/tools-config.yaml")
prod_path = Path(".tools/tools-config.yaml")

utils = ToolsUtils(dev_path, prod_path)

@click.command("model-doc")
@click.option('--is-star-statement', '-ss', is_flag=True, help="Generate documentation for a model whose last statement is a 'SELECT *' statement.")
def cli(is_star_statement):
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