from pathlib import Path
import subprocess
import yaml
from rich.console import Console

ASSETS_PATH = Path(__file__).parent.parent / "assets"

class ConfigManager:

    def __init__(self):
        self.console = Console()
        self.config_path = ASSETS_PATH / "config.yml"
        self.config = self._load_config()
        (
            self.primary_color,
            self.secondary_color,
            self.tertiary_color,
            self.quaternary_color,
            self.prompt_color,
            self.cursor_style,
            self.cursor_color,
            self.filter_prompt
        ) = self._load_theme(self.config)

    def _load_config(self):
        """Load the config.yml file."""
        try:
            with open(self.config_path, encoding="utf-8") as stream:
                try:
                    config = yaml.safe_load(stream)
                except yaml.YAMLError as exc:
                    print(exc)
        except FileNotFoundError:
            self.console.print("No config.yml File Found", style="bold red")
            exit()
        return config

    def _load_theme(self, config):
        """Load the theme file based on the name specified in the config.yml file."""
        config_theme = config["theme"]["name"]
        cmd = f"echo {config_theme}"
        theme_output = subprocess.run(
            cmd,
            shell=True,
            check=True,
            stdout=subprocess.PIPE,
            text=True
        )
        theme = theme_output.stdout.strip()
        theme_file = f"{theme}.yaml"

        try:
            theme_path = ASSETS_PATH / "themes" / theme_file
            with open(theme_path, encoding="utf-8") as stream:
                try:
                    theme = yaml.safe_load(stream)
                except yaml.YAMLError as exc:
                    print(exc)
        except FileNotFoundError:
            self.console.print("No theme file found", style="bold red")
            exit()

        return (
            theme['color_pallette']['hex_user_color'],
            theme['color_pallette']['hex_path_color'],
            theme['color_pallette']['hex_git_ref_color'],
            theme['color_pallette']['hex_branch_color'],
            theme['color_pallette']['hex_prompt_color'],
            theme['icons']['prompt_icon'],
            theme['color_pallette']['hex_user_color'],
            theme['icons']['gum_filter_icon']
        )
