from setuptools import setup

setup(
    name="iotile_support_con_nrf52832_2",
    packages=["iotile_support_con_nrf52832_2"],
    version="2.11.3",
    install_requires=['iotile_support_lib_controller_3 ~= 3.6.5'],
    entry_points={'iotile.proxy': ['nrf52832_controller = iotile_support_con_nrf52832_2.nrf52832_controller']},
    author="Arch",
    author_email="info@arch-iot.com"
)