from setuptools import setup, find_packages

setup(
    name="iotile_support_firm_accelerometer_2",
    packages=find_packages(include=["iotile_support_firm_accelerometer_2.*", "iotile_support_firm_accelerometer_2"]),
    version="2.3.0",
    install_requires=[],
    entry_points={'iotile.proxy': ['accel1_proxy = iotile_support_firm_accelerometer_2.accel1_proxy']},
    author="Arch",
    author_email="info@arch-iot.com"
)