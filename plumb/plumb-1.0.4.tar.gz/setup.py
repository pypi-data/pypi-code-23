from setuptools import setup

setup(
    name = 'plumb',
    packages = [
        'plumb',
        'plumb.aws',
        'plumb.kafka',
        'plumb.redis',
    ],
    version = '1.0.4',
    description = 'Connect systems via Kafka, Redis, AWS SQS and SNS',
    long_description=open('README.rst').read(),

    install_requires=['boto3', 'confluent_kafka==0.11.0', 'redis'],
    tests_require=['awstestutils'],

    test_suite = 'tests',

    author = 'Elvio Toccalino',
    author_email = 'elvio@spect.ro',

    keywords = ['redis', 'AWS', 'queues', 'distributed'],
    classifiers = [
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Programming Language :: Python :: 3',
        'Topic :: Utilities',
        'Topic :: System :: Networking',
        'Topic :: System :: Distributed Computing',
        'Topic :: Software Development :: Libraries',
        'Topic :: Software Development :: Object Brokering',
    ]
)
