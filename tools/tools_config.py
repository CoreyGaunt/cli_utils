import click 
from pathlib import Path
from rich.console import Console
from tools.utils.tools_utils import ToolsUtils

console = Console()

utils = ToolsUtils()

def init_tools():
    """
    This command is used to create a .tools directory in the root of the project.
    Then it will create a tools-config.yaml file in the .tools directory.
    """
    utils.check_and_install_terminal_requirements()
    config_location = Path.home() / ".tools"
    config_location.mkdir(exist_ok=True)
    team_tag = utils.init_input("What is your team's Linear Tag?", "DSA")
    team_name = utils.init_input("What is your team's name?", "Data Science & Analytics")
    with open(f"{config_location}/tools-config.yaml", "w") as file:
        file.write("general:\n")
        file.write(f'  team-tag: "{team_tag}"\n')
        file.write(f'  team-name: "{team_name}"\n')
        file.write("  raise-on-escape: true\n")
        file.write("  raise-on-interrupt: true\n")
        file.write("commits:\n")
        file.write("  conventional-commits:\n")
        file.write("    types:\n")
        file.write("      - Feat\n")
        file.write("      - Refactor\n")
        file.write("      - Fix\n")
        file.write("      - Docs\n")
        file.write("      - Style\n")
        file.write("      - Test\n")
        file.write("      - Chore\n")
        file.write("aws-info:\n")
        file.write("  dag-root: \"\"\n")
        file.write("  plugins-root: \"\"\n")
        file.write("  s3-dag-location: \"\"\n")
        file.write("  s3-plugins-location: \"\"\n")
        file.write("theme:\n")
        file.write("  name: \"iron_gold\"\n")
        file.write("excluded-commands:\n")
        file.write("  - cmd_s3-sync\n")
        file.write("  - __init__\n")
    console.print("Initialized .tools Directory", style="bold green")