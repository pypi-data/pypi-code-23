from setuptools import setup, find_packages

setup(
    name="iotile_support_con_nrf52832_2",
    packages=find_packages(include=["iotile_support_con_nrf52832_2.*", "iotile_support_con_nrf52832_2"]),
    version="2.11.4",
    install_requires=['iotile_support_lib_controller_3 ~= 3.6.5'],
    entry_points={'iotile.proxy': ['nrf52832_controller = iotile_support_con_nrf52832_2.nrf52832_controller']},
    author="Arch",
    author_email="info@arch-iot.com"
)