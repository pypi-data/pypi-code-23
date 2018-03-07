from distutils.core import setup

setup(
    name='uniboard_raspberrypi',
    version='1.0.2',
    py_modules=['uniboard_raspberrypi'],
    author='Chuan Shao',
    author_email='shaochuancs@gmail.com',
    url='https://github.com/shaochuancs/uniboard-raspberrypi',
    description='Raspberry Pi Client Uniboard',
    license='MIT',
    install_requires=['paho-mqtt']
)
