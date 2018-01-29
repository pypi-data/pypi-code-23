from distutils.core import setup

setup(
    name='rec_rnn_a3c',
    version='0.02',
    packages=['rec_rnn_a3c', 'rec_rnn_a3c.src'],
    include_package_data=True,
    install_requires=[
        'backports.weakref',
        'bleach',
        'boto3',
        'botocore',
        'docutils',
        'enum34',
        'funcsigs',
        'futures',
        'html5lib',
        'jmespath',
        'Markdown',
        'mock',
        'numpy',
        'pandas',
        'pbr',
        'protobuf',
        'python-dateutil',
        'pytz',
        's3transfer',
        'scipy',
        'six',
        'tensorflow',
        'tensorflow-tensorboard',
        'Werkzeug'
    ],
    url='',
    license='',
    author='Tim Donkers',
    author_email='tim.donkers@uni-due.de',
    description='A3C Interactive Reinforcement Learning Project'
)
