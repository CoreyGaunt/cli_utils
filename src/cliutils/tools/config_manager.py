from pathlib import Path
import yaml 
import subprocess
from rich.console import Console

class ConfigManager:

    def __init__(self):
        self.console = Console()
        self.config_path = Path.home() / ".cliutils" / "cliutils-config.yaml"
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
        """Load the cliutils-config.yaml file and set the Config.raise_on_escape and
        Config.raise_on_interrupt attributes based on the values in the config file."""
        try:
            with open(f"{self.config_path}", encoding="utf-8") as stream:
                try:
                    config = yaml.safe_load(stream)
                    # Config.raise_on_escape = config["general"]["raise-on-escape"]
                    # Config.raise_on_interrupt = config["general"]["raise-on-interrupt"]
                except yaml.YAMLError as exc:
                    print(exc)
        except FileNotFoundError:
            self.console.print("No cliutils-config.yaml File Found", style="bold red")
            exit()
        return config

    def _load_theme(self, config):
        """Load the theme file based on the name specified in the cliutils-config.yaml file."""
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
            utils_path = Path(__file__).parent
            theme_path = utils_path.parent / "themes" / theme_file
            with open(theme_path, encoding="utf-8") as stream:
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

        return (
            primary_color,
            secondary_color,
            tertiary_color,
            quaternary_color,
            prompt_color,
            cursor_style,
            cursor_color,
            filter_prompt
        )
