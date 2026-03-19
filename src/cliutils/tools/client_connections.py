import os
from rich.console import Console
from cliutils.tools import JiraClient

console = Console()

class ClientConnections:
    def __init__(self):
        self._jira = None

    @property
    def jira(self):
        if self._jira is None:
            self._jira =JiraClient(
                base_url=os.getenv("JIRA_BASE_URL"),
                email=os.getenv("JIRA_EMAIL"),
                username=os.getenv("JIRA_USERNAME"),
                api_token=os.getenv("JIRA_TOKEN"),
            )
        return self._jira

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        if self._jira:
            self._jira.close()
        return False
