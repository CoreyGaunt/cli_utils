import click # type: ignore
from cliutils.tools import (
    GumPrompts,
    ConfigManager,
    SubprocessUtilities,
)

prompts = GumPrompts()
config_manager = ConfigManager()
subprocess_utils = SubprocessUtilities()

@click.command("commit")
def commit():
    """
    Constructs a commit to your remote branch.

    This commands asks for a commit message following the Conventional Commits standards.

    The options for the commit type are stored in the config file located
    in assets/config.yml.

    The interactive prompt will ask you if you'd like to commit all of your changes. If
    you choose to commit all changes, it will add all files, ask for your commit message,
    commit the changes, and push them to the remote repository.

    If you choose not to commit all changes, it will list all the files that
    have been changed and ask you to select which files you'd like to add to the commit.

    You add a file by selecting it with the tab key. Once you've selected all the
    files you'd like to add, you can press enter to continue. It will then ask you
    for a commit message and commit the changes.
    """
    gum_confirm_output = prompts.gum_confirm("Do you want to commit all changes?")
    confirmation = gum_confirm_output

    if confirmation:
        git_add_all = "git add ."
        subprocess_utils.run(git_add_all)

        commit_type, commit_message = _generate_type_and_message()
        git_commit = f"git commit -m '{commit_type}: {commit_message}'"
        git_push = "git push"

        subprocess_utils.run(git_commit)
        subprocess_utils.run(git_push)

    else:
        # list all files that have been changed
        files = ""
        tracked_files_for_commit = ""
        changed_files = "git --no-optional-locks status --short"
        _, changed_files_output = subprocess_utils.run_and_capture_output(changed_files)
        changed_files_list = changed_files_output.split("\n")
        for file in changed_files_list:
            files += f"'{file.strip()}' "
        tracked_files = prompts.gum_filter(files, "Which File(s) Would You Like To Add?", False)
        tracked_files = [file[2:] for file in tracked_files.split("\n") if file]
        for file in tracked_files:
            tracked_files_for_commit += f"{file} "

        git_add_tracked = f"git add {tracked_files_for_commit}"
        subprocess_utils.run(git_add_tracked)

        commit_type, commit_message = _generate_type_and_message()
        git_commit = f"git commit -m '{commit_type}: {commit_message}'"
        git_push = "git push"

        subprocess_utils.run(git_commit)
        subprocess_utils.run(git_push)

def _generate_type_and_message():
    """Prompt the user to select a commit type and message."""
    commit_scopes = ""
    for scope in config_manager.config["commits"]["conventional-commits"]["types"]:
        if scope == config_manager.config["commits"]["conventional-commits"]["types"][-1]:
            commit_scopes += f"'{scope}'"
        else:
            commit_scopes += f"'{scope}' "
    commit_type = prompts.gum_filter(commit_scopes, "What Type Of Commit Is This?")
    commit_message = prompts.gum_input("What Did You Do?")

    return commit_type, commit_message
