from setuptools import setup, find_packages

setup(
    name="iotile_support_firm_env_1",
    packages=find_packages(include=["iotile_support_firm_env_1.*", "iotile_support_firm_env_1"]),
    version="1.1.1",
    install_requires=[],
    entry_points={'iotile.proxy': ['env_proxy = iotile_support_firm_env_1.env_proxy']},
    author="Arch",
    author_email="info@arch-iot.com"
)