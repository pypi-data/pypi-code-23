from setuptools import setup

setup(
    name='sca_redis_python',
    version='1.1',
    description='Provides a redis client, more specific to work with AWS Lambda',
    author='Venkatesh Kara, Sona Allahverdiyeva',
    author_email='vkara@tesla.com',
    classifiers=[
        'Programming Language :: Python :: 3.6'
    ],
    url='https://github.com/Tesla-SCA/sca_redis_python',
    packages=['redis_client'],
    install_requires=[
        'redis',
    ],
    test_suite='tests',
    include_package_data=True,
    zip_safe=False
)
