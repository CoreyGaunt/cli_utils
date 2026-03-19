import sys
import subprocess
from pathlib import Path
from rich.console import Console
from .config_manager import ConfigManager

class SubprocessUtilities:
    """This class provides utility functions for subprocesses."""
    def __init__(self):
        self.console = Console()
        self.config_manager = ConfigManager()

    def run(self, cmd):
        """Fire and forget a given shell command."""
        try:
            subprocess.run(
                cmd,
                shell=True,
                check=True,
                cwd=Path.cwd(),
            )
        except subprocess.CalledProcessError as e:
            self.console.print(
                f"Error running command: {e}",
                style=self.config_manager.quaternary_color
            )
            raise

    def run_and_capture_output(self, cmd, store_exit_code=False):
        """Run a command and return the output."""
        try:
            ran_process = subprocess.run(
                cmd,
                shell=True,
                check=True,
                cwd=Path.cwd(),
                stdout=subprocess.PIPE,
                text=True
            )

            if isinstance(ran_process, subprocess.CompletedProcess):
                output = ran_process.stdout.strip()
            else:
                output = None

            return ran_process, output

        except subprocess.CalledProcessError as e:
            if e.returncode == 130:
                self.console.print("Aborted!", style=self.config_manager.quaternary_color)
                sys.exit(1)
            if store_exit_code: # TODO: evaluate if this is actually needed
                return e.returncode, None
            else:
                sys.exit(1)
