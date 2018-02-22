from setuptools import setup

setup(
    name="iotile_support_firm_accelerometer_2",
    packages=["iotile_support_firm_accelerometer_2"],
    version="2.2.0rc2",
    install_requires=[],
    entry_points={'iotile.proxy': ['accel1_proxy = iotile_support_firm_accelerometer_2.accel1_proxy']},
    author="Arch",
    author_email="info@arch-iot.com"
)