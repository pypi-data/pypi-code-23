from setuptools import setup

setup(
    name="iotile_support_firm_env_1",
    packages=["iotile_support_firm_env_1"],
    version="1.0.2",
    install_requires=[],
    entry_points={'iotile.proxy': ['env_proxy = iotile_support_firm_env_1.env_proxy']},
    author="Arch",
    author_email="info@arch-iot.com"
)