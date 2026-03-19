from cliutils.tools import (
    ConfigManager,
    HttpClient,
)

config_manager = ConfigManager()

class JiraClient:
    def __init__(self, base_url: str, email: str, username: str, api_token: str):
        self.base_url = base_url
        self.http = HttpClient(auth=(email, api_token))
        self.username = username
        self.project = config_manager.config["general"]["team-tag"]

    def retrieve_tickets(self, current_sprint: bool = True) -> list[dict]:
        jql_query = (
            f'project = {self.project}'
            f' AND assignee = {self.username}'
            # f' AND statusCategory = "To Do"'
        )

        if current_sprint:
            jql_query += ' AND sprint in openSprints()'

        fields = ['key', 'summary']

        params = {
            'jql': jql_query,
            'fields': fields,
        }

        response = self.http.get(f'{self.base_url}/rest/api/3/search/jql', params=params)

        return self._parse_tickets(response.json())

    def _parse_tickets(self, response: list[dict]) -> list[dict]:
        return [
            {
                'key': issue.get('key'),
                'title': issue.get('fields').get('summary'),
                'slug': issue.get('key') + '-' + JiraClient._sanitize_title(issue.get('fields').get('summary'))
            }
            for issue in response.get('issues', [])
        ]

    @staticmethod
    def _sanitize_title(title_string: str) -> str:
        return title_string.replace(' ', '-').lower().replace('---', '-')

    def close(self):
        self.http.close()
