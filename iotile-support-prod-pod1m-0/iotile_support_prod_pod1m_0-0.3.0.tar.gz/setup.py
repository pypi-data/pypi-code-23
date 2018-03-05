from setuptools import setup, find_packages

setup(
    name="iotile_support_prod_pod1m_0",
    packages=find_packages(include=["iotile_support_prod_pod1m_0.*", "iotile_support_prod_pod1m_0"]),
    version="0.3.0",
    install_requires=['iotile_support_con_nrf52832_2 ~= 2.11.4', 'iotile_support_firm_accelerometer_2 ~= 2.3.1', 'iotile_support_firm_env_1 ~= 1.1.1'],
    entry_points={'iotile.app': ['tracker_app = iotile_support_prod_pod1m_0.tracker_app']},
    author="Arch",
    author_email="info@arch-iot.com"
)