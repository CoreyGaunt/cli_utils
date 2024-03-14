from setuptools import setup, find_namespace_packages
""" 
look into curses for the terminal UI

also look into this: https://github.com/charmbracelet/gum

also look into this: https://github.com/petereon/beaupy

"""

setup(
	name='cli_kit',
	version='0.1.0',
	packages=find_namespace_packages(include=['cli_kit', 'cli_kit.*']), # find_
	install_requires=[
		'click',
		'rich',
		'beaupy',
		'pyyaml'
	],
	entry_points='''
		[console_scripts]
		kit=kit:cli
	''',
)