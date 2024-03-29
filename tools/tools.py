import yaml
import click
import subprocess
import re
from pathlib import Path
from beaupy import confirm, prompt, select, select_multiple, Config
from beaupy.spinners import *
from rich.console import Console

console = Console()

dev_path = Path("./tools/tools-config.yaml")
prod_path = Path(".tools/tools-config.yaml")

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
	with open(".tools/tools-config.yaml", "w") as file:
		file.write("general:\n")
		file.write("  team-tag: \n")
		file.write("  team-name: \n")
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
		file.write("  local-dag-root: ''\n")
		file.write("  local-plugins-root: ''\n")
		file.write("  cd-dag-root: ''\n")
		file.write("  cd-plugins-root: ''\n")
		file.write("  dag-location: ''\n")
		file.write("  plugins-location: ''")
		file.write("theme:\n")
		file.write("  name: 'dusk'\n")
	console.print("Initialized .kit Directory", style="bold green")

def load_config():
	try:
		if dev_path.exists():
			file_location = dev_path
		elif prod_path.exists():
			file_location = prod_path
		else:
			raise FileNotFoundError
		with open(f"{file_location}") as stream:
			try:
				config = yaml.safe_load(stream)
				Config.raise_on_escape = config["general"]["raise-on-escape"]
				Config.raise_on_interrupt = config["general"]["raise-on-interrupt"]
				# Add new keys to the config file
				'''
				path_color=$'\e[38;2;35;75;255m' # example rgb color
				user_color=$'\e[38;2;146;9;238m' # example rgb color
				branch_color=$'\e[38;2;254;43;7m' # example rgb color
				git_ref_color=$'\e[38;2;126;254;238m' # example rgb color
				status_color=$'\e[38;2;0;171;0m' # example rgb color
				'''
			except yaml.YAMLError as exc:
				print(exc)
	except FileNotFoundError:
		console.print("No tools-config.yaml File Found", style="bold red")
		console.print("Run 'tools init' to create a tools-config.yaml file", style="cyan")
		exit()
	return config

def load_theme(config):
	
	config_theme = config["theme"]["name"]
	dev_path = "./tools/themes"
	prod_path = ".tools/themes"
	dev_theme = Path(f"{dev_path}/{config_theme}.yaml")
	prod_theme = Path(f"{prod_path}/{config_theme}.yaml")

	try:
		if dev_theme.exists():
			file_location = dev_theme
		elif prod_theme.exists():
			file_location = prod_theme
		else:
			raise FileNotFoundError
		with open(f"{file_location}") as stream:
			try:
				theme = yaml.safe_load(stream)
			except yaml.YAMLError as exc:
				print(exc)
	except FileNotFoundError:
		console.print("No theme file found", style="bold red")
		exit()

	primary_color = theme['color_pallette']['hex_user_color']
	secondary_color = theme['color_pallette']['hex_prompt_color']
	tertiary_color = theme['color_pallette']['hex_git_ref_color']
	quaternary_color = theme['color_pallette']['hex_branch_color']
	prompt_color = theme['color_pallette']['hex_path_color']
	cursor_style = theme['icons']['prompt_icon']
	cursor_color = theme['color_pallette']['hex_user_color']
	filter_prompt = theme['icons']['gum_filter_icon']
	
	return primary_color, secondary_color, tertiary_color, quaternary_color, prompt_color, cursor_style, cursor_color, filter_prompt

def remove_color_indicators(string):
	# Define a regular expression pattern to match color indicators
	rgb_pattern = r'\[/?[a-zA-Z]+\s*[a-zA-Z]*\]'
	
	# Use re.sub() to replace color indicators with an empty string
	rgb_cleaned_text = re.sub(rgb_pattern, '', string)

	# Define a regular expression pattern hex color indicators
	hex_pattern = r'\[/?#[0-9a-fA-F]+\]'

	# Use re.sub() to replace hex color indicators with an empty string
	cleaned_text = re.sub(hex_pattern, '', rgb_cleaned_text)
	
	return cleaned_text

@click.command("gum-test")
def gum_test():
	print("What is your favorite language?")
	cmd = "gum choose 'Python' 'JavaScript' 'Java' 'C++' 'C#' --item.foreground '#9209ee' --selected.foreground '#7efeee' --cursor.foreground '#7efeee'"
	subprocess.run(cmd, shell=True, check=True, cwd=Path.cwd())

@click.command("commit-all")
def commit_all():
	"""
	This command is used to commit all the changes in the current directory.
	It also asks for a commit message following the Conventional Commits standard.
	"""
	## TODO: Parameterize colors for different messages
	config = load_config()
	primary_color, secondary_color, _, _, prompt_color, cursor_style, cursor_color, _ = load_theme(config)
	commit_scopes = []
	for scope in config["commits"]["conventional-commits"]["types"]:
		commit_scopes.append(f"[{secondary_color}]{scope}[/{secondary_color}]")

	console.print("Committing All Changes", style=primary_color, highlight=True)
	commit_type = select(
		options=commit_scopes,
		cursor=cursor_style,
		cursor_style=cursor_color
		)
	# remove colors from the commit type
	commit_type = remove_color_indicators(commit_type)
	cmd1 = "git add ."
	cmd2 = f"git commit -m '{commit_type}: {prompt(f'[{prompt_color}]Enter the commit message[/{prompt_color}]')}'"
	cmd3 = "git push"
	subprocess.run(cmd1, shell=True, check=True, cwd=Path.cwd())
	subprocess.run(cmd2, shell=True, check=True, cwd=Path.cwd())
	subprocess.run(cmd3, shell=True, check=True, cwd=Path.cwd())

def commit_type_and_message():
	config = load_config()
	primary_color, secondary_color, tertiary_color, quaternary_color, prompt_color, cursor_style, cursor_color, filter_prompt = load_theme(config)
	commit_scopes = ""
	for scope in config["commits"]["conventional-commits"]["types"]:
		if scope == config["commits"]["conventional-commits"]["types"][-1]:
			commit_scopes += f"'{scope}'"
		else:
			commit_scopes += f"'{scope}' "
	gum_filter = f"gum filter {commit_scopes} --text.foreground '{secondary_color}' --indicator '{cursor_style}' --indicator.foreground '{cursor_color}'\
		--header 'What Type Of Commit Is This?' --header.foreground '{primary_color}' --prompt '{filter_prompt}' --prompt.foreground '{quaternary_color}'\
		--cursor-text.foreground '{prompt_color}' --match.foreground '{tertiary_color}' --height 10"
	commit_type_output = subprocess.run(gum_filter, shell=True, check=True, cwd=Path.cwd(), stdout=subprocess.PIPE, text=True)
	commit_type = commit_type_output.stdout.strip()
	gum_input = f"gum input --header 'What Did You Do?' --header.foreground '{primary_color}' --cursor.foreground '{cursor_color}' --prompt '{cursor_style}'\
		--prompt.foreground '{secondary_color}'"
	commit_message_output = subprocess.run(gum_input, shell=True, check=True, cwd=Path.cwd(), stdout=subprocess.PIPE, text=True)
	commit_message = commit_message_output.stdout.strip()

	return commit_type, commit_message

@click.command("gum-commit")
def gum_commit():
	"""
	This command is used to commit all the changes in the current directory.
	It also asks for a commit message following the Conventional Commits standard.
	"""
	## TODO: Parameterize colors for different messages
	config = load_config()
	primary_color, secondary_color, tertiary_color, quaternary_color, prompt_color, cursor_style, cursor_color, filter_prompt = load_theme(config)
	gum_confirm = f"gum confirm 'Do you want to commit all changes?' --prompt.foreground '{primary_color}' --selected.background '{prompt_color}'\
		--unselected.background '{secondary_color}'"
	gum_confirm_output = subprocess.run(gum_confirm, shell=True, cwd=Path.cwd(), text=True)
	if gum_confirm_output.returncode != 0:
		confirmation = False
	else:
		confirmation = True

	if confirmation:
		commit_type, commit_message = commit_type_and_message()
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
		gum_tracked_files_filter = f"gum filter {files} --text.foreground '{secondary_color}' --indicator '{cursor_style}' --indicator.foreground '{cursor_color}'\
			--header 'Which File(s) Would You Like To Add?' --header.foreground '{primary_color}' --prompt '{filter_prompt}' --prompt.foreground '{quaternary_color}'\
			--cursor-text.foreground '{prompt_color}' --match.foreground '{tertiary_color}' --height 10 --no-limit\
			--unselected-prefix.foreground '{tertiary_color}' --selected-indicator.foreground '{tertiary_color}'"
		tracked_files_output = subprocess.run(gum_tracked_files_filter, shell=True, check=True, cwd=Path.cwd(), stdout=subprocess.PIPE, text=True)
		tracked_files = tracked_files_output.stdout.strip()
		tracked_files = [file[2:] for file in tracked_files.split("\n") if file]
		for file in tracked_files:
			tracked_files_for_commit += f"{file} "
		cmd1 = f"git add {tracked_files_for_commit}"
		commit_message, commit_type = commit_type_and_message()
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
	config = load_config()
	config = load_config()
	primary_color, secondary_color, _, _, prompt_color, cursor_style, cursor_color, _ = load_theme(config)
	console.print("Syncing Local Data With S3 Bucket", style=primary_color, highlight=True)
	sources = [
		f"[{secondary_color}]{config['aws-info']['cd-dag-root']}[/{secondary_color}]",
		f"[{secondary_color}]{config['aws-info']['cd-plugins-root']}[/{secondary_color}]",
		f"[{secondary_color}]{config['aws-info']['local-dag-root']}[/{secondary_color}]",
		f"[{secondary_color}]{config['aws-info']['local-plugins-root']}[/{secondary_color}]"
	]
	targets = [
		f"[{secondary_color}]{config['aws-info']['dag-location']}[/{secondary_color}]",
		f"[{secondary_color}]{config['aws-info']['plugins-location']}[/{secondary_color}]"
	]

	source_selection = select(
		options=sources,
		cursor=cursor_style,
		cursor_style=cursor_color
		)
	source_selection = remove_color_indicators(source_selection)

	target_selection = select(
		options=targets,
		cursor=cursor_style,
		cursor_style=cursor_color
		)
	target_selection = remove_color_indicators(target_selection)

	confirmation = confirm(
		question=f"[{prompt_color}]Are you sure you want to sync {source_selection} with {target_selection}?[/{prompt_color}]",
		yes_text="I am sure, sync it",
		no_text="Nope! Go back!",
		cursor=cursor_style,
		cursor_style=cursor_color)
	if confirmation:
		cmd = f"aws s3 sync {source_selection} {target_selection} --exclude '**/.DS_Store' --exclude '**/__pycache__/**' --exclude '.DS_Store'"
		subprocess.run(cmd, shell=True, check=True, cwd=Path.cwd())
	else:
		console.print("Sync Cancelled", style="bold red")

@click.command("branch-new")
def branch_new():
	"""
	This command is used to create a new branch.
	"""
	config = load_config()
	config = load_config()
	primary_color, secondary_color, _, _, prompt_color, cursor_style, cursor_color, _ = load_theme(config)
	console.print("Creating a New Branch", style=primary_color, highlight=True)
	branch_prefixes = []
	for prefix in config['branches']['branch-prefixes']:
		branch_prefixes.append(f"[{secondary_color}]{prefix}[/{secondary_color}]")
	branch_type = select(
		options=branch_prefixes,
		cursor=cursor_style,
		cursor_style=cursor_color
		)
	branch_type = remove_color_indicators(branch_type)
	has_corresponding_ticket = confirm(
		question=f"[{prompt_color}]Does this branch have a corresponding Linear ticket?[/{prompt_color}]",
		cursor=cursor_style,
		cursor_style=cursor_color
		)
	if has_corresponding_ticket:
		ticket_number = prompt(f"[{prompt_color}]Enter the ticket number[/{prompt_color}]")
		ticket_number = remove_color_indicators(ticket_number)
		branch_ticket_ref = f"{config['general']['team-tag']}-{ticket_number}"
	branch_name = prompt(f"[{prompt_color}]Enter the branch name[/{prompt_color}]")
	branch_name = remove_color_indicators(branch_name)
	cmd1 = "git checkout main && git pull"
	if has_corresponding_ticket:
		cmd2 = f"git checkout -b {branch_type}/{branch_ticket_ref}-{branch_name} && git push --set-upstream origin {branch_type}/{branch_ticket_ref}-{branch_name}"
	else:
		cmd2 = f"git checkout -b {branch_type}/{branch_name} && git push --set-upstream origin {branch_type}/{branch_name}"
	spinner = Spinner(LOADING, "	  Pulling Down From Main")
	spinner.start()
	subprocess.run(cmd1, shell=True, check=True, cwd=Path.cwd(), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
	subprocess.run(cmd2, shell=True, check=True, cwd=Path.cwd(), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
	spinner.stop()
	
	

cli.add_command(init)
cli.add_command(commit_all)
cli.add_command(dsa_s3_sync)
cli.add_command(branch_new)
cli.add_command(gum_test)
cli.add_command(gum_commit)