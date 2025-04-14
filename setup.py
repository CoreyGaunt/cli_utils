from pathlib import Path
from setuptools import setup, find_packages, find_namespace_packages

""" 
look into curses for the terminal UI

also look into this: https://github.com/charmbracelet/gum

also look into this: https://github.com/petereon/beaupy

read through this whenever you want to update this file:
https://click.palletsprojects.com/en/8.1.x/setuptools/

read through here for autocomplete specs:
https://fig.io/docs/getting-started/first-completion-spec

"""

setup(
	name='tools',
	version='0.3.0',
	packages=find_namespace_packages(include=["tools", "tools*"]),
	package_data={"": ["*.yaml", "*.txt", "*.md"]},
	author="Corey Gaunt",
	url="https://github.com/CoreyGaunt/cli_utils",
	entry_points='''
		[console_scripts]
		tools=tools.cli:cli
	''',
	install_requires=Path("requirements.txt").read_text().splitlines(),
)
