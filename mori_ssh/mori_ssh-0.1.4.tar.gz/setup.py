from setuptools import setup, find_packages

setup(
    name='mori_ssh',
    version='0.1.4',
    description='Mori SSH pack',
    author='moridisa',
    author_email='moridisa@moridisa.cn',
    url='https://github.com/moriW/mssh',
    license='MIT',
    py_modules=['mori_ssh'],
    entry_points={
        'console_scripts': [
            'mssh=mori_ssh:main',
        ]
    },
    packages=find_packages(),
    install_requires=[
        'pexpect'
    ],
)
