from setuptools import setup

setup(
    name='indico-wp',
    version='0.1.0.dev7',
    description='A tool for a wordpress server which will automatically post science events from indico website',
    url='https://github.com/the16thpythonist/IndicoWp',
    author='Jonas Teufel',
    author_email='jonseb1998@gmail.com',
    license='MIT',
    packages=['IndicoWp', 'IndicoWp/indico', 'IndicoWp/views', 'IndicoWp/tests', 'IndicoWp/templates'],
    include_package_data=False,
    install_requires=[
        'requests>=2.0',
        'mysqlclient>=1.2',
        'jinja2>=2.2',
        'SQLAlchemy>=1.2',
        'tabulate>=0.8',
        'python-wordpress-xmlrpc>=2.3'
    ],
    data_files=[('', ['/home/jonas/PycharmProjects/IndicoWp/IndicoWp/templates/post.html'])],
    python_requires='>=3, <4',
)
