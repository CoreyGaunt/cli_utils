import click
import subprocess
from pathlib import Path
from tools.utils.tools_utils import ToolsUtils

utils = ToolsUtils()

@click.command("commit")
def cli():
	"""
	Constructs a commit to your remote branch.

	This commands asks for a commit message following the Conventional Commits standards. The options for the commit type are stored in the user's home .tools/tools-config.yaml file.

	The interactive prompt will ask you if you'd like to commit all of your changes. If you choose to commit all changes, it will add all files, ask for your commit message, commit the changes, and push them to the remote repository.
	If you choose not to commit all changes, it will list all the files that have been changed and ask you to select which files you'd like to add to the commit.

	You add a file by selecting it with the tab key. Once you've selected all the files you'd like to add, you can press enter to continue. It will then ask you for a commit message and commit the changes.
	"""
	config = utils.load_config()
	gum_confirm_output = utils.gum_confirm("Do you want to commit all changes?")
	confirmation = gum_confirm_output

	if confirmation:
		commit_type, commit_message = utils.commit_type_and_message()
		cmd1 = "git add ."
		cmd2 = f"git commit -m '{commit_type}: {commit_message}'"
		cmd3 = "git push"
		# cmd4 = "make build"
		subprocess.run(cmd1, shell=True, check=True, cwd=Path.cwd())
		subprocess.run(cmd2, shell=True, check=True, cwd=Path.cwd())
		subprocess.run(cmd3, shell=True, check=True, cwd=Path.cwd())
		# subprocess.run(cmd4, shell=True, check=True, cwd=Path.cwd())
	else:
		# list all files that have been changed
		files = ""
		tracked_files_for_commit = ""
		changed_files = "git --no-optional-locks status --short"
		changed_files_output = subprocess.run(changed_files, shell=True, check=True, cwd=Path.cwd(), stdout=subprocess.PIPE, text=True)
		changed_files_list = changed_files_output.stdout.strip().split("\n")
		for file in changed_files_list:
			files += f"'{file.strip()}' "
		tracked_files = utils.gum_filter(files, "Which File(s) Would You Like To Add?", False)
		tracked_files = [file[2:] for file in tracked_files.split("\n") if file]
		for file in tracked_files:
			tracked_files_for_commit += f"{file} "
		cmd1 = f"git add {tracked_files_for_commit}"
		commit_type, commit_message = utils.commit_type_and_message()
		cmd2 = f"git commit -m '{commit_type}: {commit_message}'"
		cmd3 = "git push"
		# cmd4 = "make build"
		subprocess.run(cmd1, shell=True, check=True, cwd=Path.cwd())
		subprocess.run(cmd2, shell=True, check=True, cwd=Path.cwd())
		subprocess.run(cmd3, shell=True, check=True, cwd=Path.cwd())
		# subprocess.run(cmd4, shell=True, check=True, cwd=Path.cwd())