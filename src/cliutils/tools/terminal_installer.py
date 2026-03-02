import subprocess
from pathlib import Path
from rich.console import Console

ASSETS_PATH = Path(__file__).parent.parent / "assets"

class TerminalInstaller:
    """This class provides utility functions for the cliutils 
    command."""
    def __init__(self):
        self.console = Console()
        self.config_path = ASSETS_PATH / "config.yml"

    def check_and_install_terminal_requirements(self):
        """Check and install the terminal requirements for the cliutils command."""
        # Check if Homebrew is installed, if not install it
        homebrew_check = subprocess.run(
            "brew --version", 
            shell=True,
            check=False,
            stdout=subprocess.PIPE,
            text=True
        )
        if homebrew_check.returncode != 0:
            self.console.print(
                "Homebrew Not Found, Installing Homebrew",
                style="bold red"
            )
            homebrew_install_url = (
                "https://raw.githubusercontent.com/Homebrew/install/"
                "HEAD/install.sh"
            )
            subprocess.run(
                f"/bin/bash -c \"$(curl -fsSL {homebrew_install_url})\"",
                shell=True,
                check=True,
                stdout=subprocess.PIPE,
                text=True
            )
            self.console.print("Homebrew Installed", style="bold green")
        else:
            self.console.print("Homebrew Found", style="bold green")
        # Check if Gum is installed, if not install it
        gum_check = subprocess.run(
            "gum --version", 
            shell=True,
            check=False,
            stdout=subprocess.PIPE,
            text=True
        )
        if gum_check.returncode != 0:
            self.console.print("Gum Not Found, Installing Gum", style="bold red")
            subprocess.run(
                "brew install gum", 
                shell=True,
                check=True,
                stdout=subprocess.PIPE,
                text=True
            )
            self.console.print("Gum Installed", style="bold green")
        else:
            self.console.print("Gum Found", style="bold green")
