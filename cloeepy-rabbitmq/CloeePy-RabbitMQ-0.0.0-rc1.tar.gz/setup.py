from distutils.core import setup

setup(
    name='CloeePy-RabbitMQ',
    version='0.0.0-rc1',
    packages=['cloeepy_rabbitmq',],
    package_data = {
        'cloeepy_rabbitmq': ['data/*.yml'],
    },
    license='MIT',
    description="RabbitMQ Plugin for CloeePy Framework",
    long_description=open('README.md').read(),
    install_requires=[
        "pika>=0,<1",
        "CloeePy>=0",
     ],
     url = "https://github.com/cloeeai/CloeePy-RabbitMQ",
     author = "Scott Crespo",
     author_email = "sccrespo@gmail.com",
     keywords = "mini framework cloee cloeepy rabbitmq",
     python_requires='~=3.3',
)
