from setuptools import setup, find_packages


setup(
	name="smsactivateapitesto",
	version="0.2",
	author="cyla productions",
	packages=find_packages(),
	author_email="cylagram@gmail.com",
	description="smsactivateapi to management of your personal account!",
	scripts=["sms-activate.py"],
	install_requires=["requests>=2.0"]
)