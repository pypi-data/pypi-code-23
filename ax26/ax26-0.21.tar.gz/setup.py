from distutils.core import setup
setup(
	name = 'ax26',
	packages = ['ax26'],
	version = '0.21',
	description = 'AX26 Client/Server library in Python.',
	author = 'Stephen Downward',
	author_email = 'stephen@stephendownward.ca',
	url = 'https://git.scd31.com/laptopdude90/ax26',
	keywords = ['ham radio', 'ax26', 'packet', 'KISS'],
	classifiers = [],
	install_requires = ["kiss2 > 7.0.0"]
)