from setuptools import setup, find_packages

setup(
	name='project1',
	version='1.0',
	author='Prajay Yalamanchili',
	authour_email='16891669',
	packages=find_packages(exclude=('tests', 'docs')),
	setup_requires=['pytest-runner'],
	tests_require=['pytest']
)