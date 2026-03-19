import sys
import click
from cliutils.tools import (
    GumPrompts,
    ConfigManager,
    SubprocessUtilities,
    ClientConnections,
)

prompts = GumPrompts()
config_manager = ConfigManager()
subprocess_utils = SubprocessUtilities()

# TODO: Refactor using Gum commands
@click.command("branch-new")
def branch_new():
    with ClientConnections() as clients:
        tickets = clients.jira.retrieve_tickets()
        if not tickets:
            print("No tickets found")
            sys.exit(1)

    ticket_titles = [ticket['title'] for ticket in tickets]
    ticket_titles_string = " ".join([f"'{ticket}'" for ticket in ticket_titles])
    selected_ticket = prompts.gum_filter(ticket_titles_string, "Select a ticket")

    ticket_slug = [ ticket['slug'] for ticket in tickets if ticket['title'] == selected_ticket ]

    _, pull_default_branch_name = subprocess_utils.run_and_capture_output(
        "git rev-parse --abbrev-ref origin/HEAD"
    )
    default_branch = pull_default_branch_name.replace("origin/", "")

    subprocess_utils.run(f"git checkout {default_branch} && git pull")

    branch_creation_command = (
        f'git checkout -b {ticket_slug}\
            && git push --set-upstream origin {ticket_slug}'
    )

    subprocess_utils.run(branch_creation_command)
