import requests
from rich.console import Console

console = Console()

class HttpClient:
    def __init__(self, headers: dict = None, auth: tuple = None, timeout: int = 10):
        self.session = requests.Session()
        self.timeout = timeout

        default_headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

        if headers:
            default_headers.update(headers)

        self.session.headers.update(default_headers)

        if auth:
            self.session.auth = auth

    def get(self, url: str, params: dict = None) -> requests.Response:
        try:
            response = self.session.get(url, params=params, timeout=self.timeout)
            response.raise_for_status()
            return response
        except requests.exceptions.HTTPError as e:
            console.print(f"[bold red]HTTP error:[/bold red] {e.response.status_code} — {url}")
            raise
        except requests.exceptions.ConnectionError:
            console.print(f"[bold red]Connection error:[/bold red] Could not reach {url}")
            raise
        except requests.exceptions.Timeout:
            console.print(f"[bold red]Timeout:[/bold red] Request to {url} timed out")
            raise

    def post(self, url: str, payload: dict = None) -> requests.Response:
        try:
            response = self.session.post(url, json=payload, timeout=self.timeout)
            response.raise_for_status()
            return response
        except requests.exceptions.HTTPError as e:
            console.print(f"[bold red]HTTP error:[/bold red] {e.response.status_code} — {url}")
            raise
        except requests.exceptions.ConnectionError:
            console.print(f"[bold red]Connection error:[/bold red] Could not reach {url}")
            raise
        except requests.exceptions.Timeout:
            console.print(f"[bold red]Timeout:[/bold red] Request to {url} timed out")
            raise

    def close(self):
        self.session.close()
