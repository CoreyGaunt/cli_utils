import os 
import re
import yaml
import subprocess
import pkg_resources
from pathlib import Path
from rich.console import Console
from beaupy import confirm, prompt, select, Config

class ToolsUtils:
	def __init__(self):
		self.console = Console()
		self.config_path = Path.home() / ".tools" / "tools-config.yaml"

	def check_and_install_terminal_requirements(self):
		# Check if Homebrew is installed, if not install it
		homebrew_check = subprocess.run("brew --version", shell=True, check=False, stdout=subprocess.PIPE, text=True)
		if homebrew_check.returncode != 0:
			self.console.print("Homebrew Not Found, Installing Homebrew", style="bold red")
			subprocess.run("/bin/bash -c \"$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)\"", shell=True, check=True, stdout=subprocess.PIPE, text=True)
			self.console.print("Homebrew Installed", style="bold green")
		else:
			self.console.print("Homebrew Found", style="bold green")
		# Check if Gum is installed, if not install it
		gum_check = subprocess.run("gum --version", shell=True, check=False, stdout=subprocess.PIPE, text=True)
		if gum_check.returncode != 0:
			self.console.print("Gum Not Found, Installing Gum", style="bold red")
			subprocess.run("brew install gum", shell=True, check=True, stdout=subprocess.PIPE, text=True)
			self.console.print("Gum Installed", style="bold green")
		else:
			self.console.print("Gum Found", style="bold green")
			
	def add_cmd_to_zsh_history(self, cmd):
		with open(Path.home() / ".zsh_history", "a") as history_file:
			history_file.write(f"{cmd}\n")
		os.system("exec zsh -l")

	def find_all_files_in_directory(self, language, directory, file_type):
		if language == "python":
			model_list = []
		elif language == "zsh":
			model_list = ""
		models = subprocess.run(f"find {directory} -type f -name '*.{file_type}' -exec basename {{}} .sql \;", shell=True, check=True, stdout=subprocess.PIPE, text=True)
		models = models.stdout.strip().split("\n")
		for model in models:
			if language == "python":
				model_list.append(model)
			elif language == "zsh":
				model_list += f"'{model}' "
		
		return model_list

	def load_config(self):
		try:
			if self.config_path.exists():
				file_location = self.config_path
			with open(f"{file_location}") as stream:
				try:
					config = yaml.safe_load(stream)
					Config.raise_on_escape = config["general"]["raise-on-escape"]
					Config.raise_on_interrupt = config["general"]["raise-on-interrupt"]
				except yaml.YAMLError as exc:
					print(exc)
		except:
			self.console.print("No tools-config.yaml File Found", style="bold red")
			self.console.print("Run 'tools init' to create a tools-config.yaml file", style="cyan")
			exit()
		return config
	
	def load_theme(self, config):
	
		config_theme = config["theme"]["name"]
		cmd = f"echo {config_theme}"
		theme_output = subprocess.run(cmd, shell=True, check=True, stdout=subprocess.PIPE, text=True)
		theme = theme_output.stdout.strip()
		theme_file = f"{theme}.yaml"
		

		try:
			utils_path = Path(pkg_resources.resource_filename(__name__, ''))
			theme_path = utils_path.parent / "themes" / theme_file
			with open(theme_path) as stream:
				try:
					theme = yaml.safe_load(stream)
				except yaml.YAMLError as exc:
					print(exc)
		except FileNotFoundError:
			self.console.print("No theme file found", style="bold red")
			exit()

		primary_color = theme['color_pallette']['hex_user_color']
		secondary_color = theme['color_pallette']['hex_path_color']
		tertiary_color = theme['color_pallette']['hex_git_ref_color']
		prompt_color = theme['color_pallette']['hex_prompt_color']
		quaternary_color = theme['color_pallette']['hex_branch_color']
		cursor_style = theme['icons']['prompt_icon']
		cursor_color = theme['color_pallette']['hex_user_color']
		filter_prompt = theme['icons']['gum_filter_icon']
		
		return primary_color, secondary_color, tertiary_color, quaternary_color, prompt_color, cursor_style, cursor_color, filter_prompt
	
	def remove_color_indicators(self, string):
		# Define a regular expression pattern to match color indicators
		rgb_pattern = r'\[/?[a-zA-Z]+\s*[a-zA-Z]*\]'
		
		# Use re.sub() to replace color indicators with an empty string
		rgb_cleaned_text = re.sub(rgb_pattern, '', string)

		# Define a regular expression pattern hex color indicators
		hex_pattern = r'\[/?#[0-9a-fA-F]+\]'

		# Use re.sub() to replace hex color indicators with an empty string
		cleaned_text = re.sub(hex_pattern, '', rgb_cleaned_text)
		
		return cleaned_text
	
	def commit_type_and_message(self):
		config = self.load_config()
		commit_scopes = ""
		for scope in config["commits"]["conventional-commits"]["types"]:
			if scope == config["commits"]["conventional-commits"]["types"][-1]:
				commit_scopes += f"'{scope}'"
			else:
				commit_scopes += f"'{scope}' "
		commit_type = self.gum_filter(commit_scopes, "What Type Of Commit Is This?")
		commit_message = self.gum_input("What Did You Do?")

		return commit_type, commit_message
	
	def gum_filter(self, filter_list, header, has_limit=True):
		config = self.load_config()
		primary_color, secondary_color, tertiary_color, quaternary_color, prompt_color, cursor_style, cursor_color, filter_prompt = self.load_theme(config)
		if has_limit:
			gum_filter = f"gum filter {filter_list} --text.foreground '{prompt_color}' --indicator '{cursor_style}' --indicator.foreground '{cursor_color}'\
				--header '{header}' --header.foreground '{primary_color}' --prompt '{filter_prompt}' --prompt.foreground '{quaternary_color}'\
				--cursor-text.foreground '{secondary_color}' --match.foreground '{tertiary_color}' --height 10\
				--unselected-prefix.foreground '{tertiary_color}' --selected-indicator.foreground '{tertiary_color}'"
		else:
			gum_filter = f"gum filter {filter_list} --text.foreground '{prompt_color}' --indicator '{cursor_style}' --indicator.foreground '{cursor_color}'\
			--header '{header}' --header.foreground '{primary_color}' --prompt '{filter_prompt}' --prompt.foreground '{quaternary_color}'\
			--cursor-text.foreground '{secondary_color}' --match.foreground '{tertiary_color}' --height 10 --no-limit\
			--unselected-prefix.foreground '{tertiary_color}' --selected-indicator.foreground '{tertiary_color}'"
		gum_filter_process = subprocess.run(gum_filter, shell=True, check=True, cwd=Path.cwd(), stdout=subprocess.PIPE, text=True)
		gum_filter_output = gum_filter_process.stdout.strip()

		return gum_filter_output
	
	def gum_input(self, header, placeholder=None):
		config = self.load_config()
		primary_color, secondary_color, tertiary_color, quaternary_color, prompt_color, cursor_style, cursor_color, filter_prompt = self.load_theme(config)
		if placeholder:
			pass 
		else:
			placeholder = ""
		sanitize_header = header.replace("'", "'\\''")
		sanitize_placeholder = placeholder.replace("'", "'\\''")
		gum_input = f"gum input --header '{sanitize_header}' --width 65 --header.foreground '{primary_color}' --cursor.foreground '{cursor_color}' --prompt '{cursor_style}'\
			--prompt.foreground '{prompt_color}' --value '{sanitize_placeholder}'"
		gum_input_process = subprocess.run(gum_input, shell=True, check=True, cwd=Path.cwd(), stdout=subprocess.PIPE, text=True)
		gum_input_output = gum_input_process.stdout.strip()

		return gum_input_output
	
	def init_input(self, header, placeholder=None):
		if placeholder:
			pass 
		else:
			placeholder = ""
		sanitize_header = header.replace("'", "'\\''")
		sanitize_placeholder = placeholder.replace("'", "'\\''")
		gum_input = f"gum input --header '{sanitize_header}' --width 65 --value '{sanitize_placeholder}'"
		gum_input_process = subprocess.run(gum_input, shell=True, check=True, cwd=Path.cwd(), stdout=subprocess.PIPE, text=True)
		gum_input_output = gum_input_process.stdout.strip()

		return gum_input_output
	
	def gum_confirm(self, message):
		config = self.load_config()
		primary_color, secondary_color, tertiary_color, quaternary_color, prompt_color, cursor_style, cursor_color, filter_prompt = self.load_theme(config)
		gum_confirm = f"gum confirm '{message}' --prompt.foreground '{primary_color}'\
		--selected.background '{secondary_color}' --unselected.background '{tertiary_color}'"
		try:
			subprocess.run(gum_confirm, shell=True, check=True, cwd=Path.cwd(), stdout=subprocess.PIPE, text=True)
			gum_confirm_output = True 
		except subprocess.CalledProcessError:
			gum_confirm_output = False

		return gum_confirm_output
	
	def gum_choose(self, choices):
		config = self.load_config()
		primary_color, secondary_color, tertiary_color, quaternary_color, prompt_color, cursor_style, cursor_color, filter_prompt = self.load_theme(config)
		gum_choose = f"gum choose {choices} --ordered --cursor '{cursor_style}' --cursor.foreground '{quaternary_color}'\
		--item.foreground '{tertiary_color}'"
		gum_choose_process = subprocess.run(gum_choose, shell=True, check=True, cwd=Path.cwd(), stdout=subprocess.PIPE, text=True)
		gum_choose_output = gum_choose_process.stdout.strip()

		return gum_choose_output
	
	def gum_write(self, header, templated_text=None):
		config = self.load_config()
		primary_color, secondary_color, tertiary_color, quaternary_color, prompt_color, cursor_style, cursor_color, filter_prompt = self.load_theme(config)
		if templated_text:
			body_from_env = templated_text
		else:
			body_from_env = " "
		gum_write = f"gum write --header '{header}' --header.foreground '{primary_color}' --cursor.foreground '{cursor_color}'\
		--prompt.foreground '{secondary_color}' --char-limit 0 --value '{body_from_env}' --width 65 --height 10"
		gum_write_process = subprocess.run(gum_write, shell=True, check=True, cwd=Path.cwd(), stdout=subprocess.PIPE, text=True)
		gum_write_output = gum_write_process.stdout.strip()

		return gum_write_output