import codecs
from setuptools import setup, find_packages


entry_points = {
    "zc.buildout": [
        'default = nti.recipes.passwords:DecryptSection',
        'decryptFile = nti.recipes.passwords:DecryptFile'
    ],
}

TESTS_REQUIRE = [
    'pyhamcrest',
    'zope.testrunner',
    'fudge',
]


def _read(fname):
    with codecs.open(fname, encoding='utf-8') as f:
        return f.read()


setup(
    name='nti.recipes.passwords',
    version='1.0.0',
    author='Jason Madden',
    author_email='open-source@nextthought.com',
    description="zc.buildout recipes for securely storing passwords in version control",
    long_description=(_read('README.rst') + '\n\n' + _read("CHANGES.rst")),
    license='Apache',
    url="https://github.com/NextThought/nti.recipes.passwords",
    keywords='buildout password',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: PyPy',
        'Framework :: Buildout',
    ],
    zip_safe=True,
    packages=find_packages('src'),
    package_dir={'': 'src'},
    include_package_data=True,
    namespace_packages=['nti', 'nti.recipes'],
    tests_require=TESTS_REQUIRE,
    install_requires=[
        'setuptools',
        'zc.buildout',
        'zc.recipe.deployment',
        'cryptography',
    ],
    extras_require={
        'test': TESTS_REQUIRE,
    },
    entry_points=entry_points,
)
