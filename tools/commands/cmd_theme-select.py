import click
import subprocess
from pathlib import Path
from rich.console import Console
from tools.utils.tools_utils import ToolsUtils

console = Console()
utils = ToolsUtils()

@click.command("theme-select")
def cli():
	"""
	Select a color theme for your Tools package in the terminal.

	The default them is 'iron gold'. The available themes are stored in the tools package. The command will prompt you to select a theme from the available options to use as your color theme.
	"""
	config = utils.load_config()
	themes_list = ""
	primary_color, secondary_color, tertiary_color, quaternary_color, prompt_color, cursor_style, cursor_color, filter_prompt = utils.load_theme(config)
	themes_dir = Path(__file__).parent.parent / "themes"
	themes = utils.find_all_files_in_directory('python', themes_dir, 'yaml')
	for theme in themes:
		themes_list += f"'{theme[:-5]}' "
	theme_name = utils.gum_filter(themes_list, "Select A Theme")
	tools_config_loc = Path.home() / ".tools" / "tools-config.yaml"
	cmd = f'''awk '/theme:/ {{c=1}} c && /name:/ {{sub(/name: .*/, "name: \\"{theme_name}\\""); c=0}} 1' {tools_config_loc} > temp && mv temp {tools_config_loc}'''
	subprocess.run(cmd, shell=True, check=True)
	console.print(f"Theme {theme_name} selected", style="bold green")
