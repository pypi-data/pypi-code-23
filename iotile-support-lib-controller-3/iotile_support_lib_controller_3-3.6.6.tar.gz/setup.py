from setuptools import setup

setup(
    name="iotile_support_lib_controller_3",
    packages=["iotile_support_lib_controller_3"],
    version="3.6.6",
    install_requires=[],
    entry_points={'iotile.proxy_plugin': ['configmanager = iotile_support_lib_controller_3.configmanager', 'sensorgraph = iotile_support_lib_controller_3.sensorgraph', 'controllertest = iotile_support_lib_controller_3.controllertest', 'tilemanager = iotile_support_lib_controller_3.tilemanager', 'remotebridge = iotile_support_lib_controller_3.remotebridge'], 'iotile.type_package': ['lib_controller_types = iotile_support_lib_controller_3.lib_controller_types']},
    author="Arch",
    author_email="info@arch-iot.com"
)