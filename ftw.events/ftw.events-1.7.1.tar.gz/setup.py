from setuptools import setup, find_packages
import os

version = '1.7.1'

tests_require = [
    'collective.taskqueue',
    'ftw.builder',
    'ftw.chameleon',
    'ftw.events[mopage_publisher_receiver]',
    'ftw.lawgiver',
    'ftw.testbrowser',
    'ftw.testing',
    'plone.app.testing',
    'plone.testing',
]

extras_require = {
    'tests': tests_require,
    'development': [
        'plonetheme.blueberry',
        'ftw.events[mopage_publisher_receiver]',
    ],

    # The mopage_publisher_receiver should be installed on a ftw.publisher
    # receiver installation in order to enable the mopage trigger function.
    # It should *NOT* be installed on ftw.pubsliher.sender site, since
    # the trigger will then be triggered too early.
    'mopage_publisher_receiver': [
        'collective.taskqueue',
        'ftw.publisher.receiver',
        'requests',
    ],
}

setup(
    name='ftw.events',
    version=version,
    description='Events with simplelayout.',
    long_description=open('README.rst').read() + '\n' + open(
        os.path.join('docs', 'HISTORY.txt')).read(),

    classifiers=[
        'Framework :: Plone',
        'Framework :: Plone :: 4.3',
        'License :: OSI Approved :: GNU General Public License (GPL)',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],

    keywords='ftw events',
    author='4teamwork AG',
    author_email='mailto:info@4teamwork.ch',
    url='https://github.com/4teamwork/ftw.events',
    license='GPL2',

    packages=find_packages(exclude=['ez_setup']),
    namespace_packages=['ftw', ],
    include_package_data=True,
    zip_safe=False,

    install_requires=[
        'Plone',
        'collective.dexteritytextindexer',
        'ftw.autofeature',
        'ftw.keywordwidget',
        'ftw.profilehook',
        'ftw.referencewidget',
        'ftw.simplelayout [contenttypes] >= 1.14.0',
        'ftw.upgrade',
        'plone.api',
        'plone.app.dexterity',
        'plone.app.event [dexterity]',
        'plone.app.referenceablebehavior',
        'plone.directives.form',
        'setuptools',
    ],

    tests_require=tests_require,
    extras_require=extras_require,

    entry_points="""
    # -*- Entry points: -*-
    [z3c.autoinclude.plugin]
    target = plone
    """)
