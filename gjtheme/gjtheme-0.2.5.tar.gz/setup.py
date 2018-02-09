import io
import setuptools as st

import gjtheme

with io.open('README.rst', encoding='UTF-8') as reader:
    readme = reader.read()

st.setup(
    name='gjtheme',
    version=gjtheme.__version__,
    description='Sphinx GJ Theme',
    long_description=readme,
    author='Grant Jenks',
    author_email='contact@grantjenks.com',
    url='http://www.grantjenks.com/docs/gjtheme/',
    packages=['gjtheme'],
    include_package_data=True,
    entry_points = {
        'sphinx.html_themes': [
            'gjtheme = gjtheme',
        ],
    },
    license='Apache 2.0',
    install_requires=[],
    classifiers=(
        'Development Status :: 4 - Beta',
        'License :: OSI Approved :: Apache Software License',
        'Natural Language :: English',
        'Programming Language :: Python',
    ),
)
