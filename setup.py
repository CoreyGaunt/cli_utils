from setuptools import setup, find_packages
""" 
look into curses for the terminal UI

also look into this: https://github.com/charmbracelet/gum

also look into this: https://github.com/petereon/beaupy

read through this whenever you want to update this file:
https://click.palletsprojects.com/en/8.1.x/setuptools/

"""

setup(
	name='ae-kit',
	version='0.2.0',
	packages=find_packages(),
	include_package_data=True,
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
		ae-kit=ae-kit.ae-kit:cli
	''',
)