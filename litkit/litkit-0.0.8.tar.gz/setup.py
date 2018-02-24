from distutils.core import setup

setup(
    name='litkit',
    packages=['litkit'],
    version='0.0.8',
    description='data analysis convenience package',
    author='Philipp Woerdehoff',
    author_email='ph.woerdehoff@gmail.com',
    include_package_data=True,
    url='https://github.com/21stio/litkit',
    download_url='https://github.com/21stio/litkit/archive/0.1.tar.gz',
    keywords=['pandas', 'scikit', 'plotly'],
    package_data={'litkit':['*', '*/*', '*/*/*']},
    classifiers=[],
)