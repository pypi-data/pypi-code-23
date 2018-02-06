from setuptools import setup, find_packages


setup(
	name="smsactivateapi",
	version="0.1.0",
	author="cyla productions",
	packages=find_packages(),
	author_email="cylagram@gmail.com",
	description="smsactivateapi to management of your personal account!",
	scripts=["sms-activate.py"],
	install_requires=["requests>=2.0"]
)