from setuptools import setup, find_namespace_packages
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
	name='ae-kit',
	version='0.1.0',
	packages=find_namespace_packages(include=['ae_kit', 'ae_kit.*']),
	package_data={"": ["*.yaml"]},
	author="Corey Gaunt",
	url="https://github.com/CoreyGaunt/cli_utils",
	install_requires=[
		'click',
		'rich',
		'beaupy',
		'pyyaml'
	],
	entry_points='''
		[console_scripts]
		ae-kit=ae_kit.ae_kit:cli
	''',
)