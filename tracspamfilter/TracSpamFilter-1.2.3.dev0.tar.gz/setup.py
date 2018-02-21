#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2006-2015 Edgewall Software
# All rights reserved.
#
# This software is licensed as described in the file COPYING, which
# you should have received as part of this distribution. The terms
# are also available at http://trac.edgewall.com/license.html.
#
# This software consists of voluntary contributions made by many
# individuals. For the exact contribution history, see the revision
# history and logs, available at http://projects.edgewall.com/trac/.

from setuptools import setup, find_packages

PACKAGE = 'TracSpamFilter'
VERSION = '1.2.3'

extra = {}
try:
    from trac.util.dist import get_l10n_cmdclass
    cmdclass = get_l10n_cmdclass()
    if cmdclass:
        extra['cmdclass'] = cmdclass
        extractors = [
            ('**.py',                'trac.dist:extract_python', None),
            ('**/templates/**.html', 'genshi', None)
        ]
        extra['message_extractors'] = {
            'tracspamfilter': extractors,
        }
except ImportError:
    pass

setup(
    name=PACKAGE,
    version=VERSION,
    description='Plugin for spam filtering',
    author="Edgewall Software",
    author_email="info@edgewall.com",
    url='http://trac.edgewall.org/wiki/SpamFilter',
    download_url='http://trac.edgewall.org/wiki/SpamFilter',
    license='BSD',
    classifiers=[
        'Framework :: Trac',
        'License :: OSI Approved :: BSD License',
    ],
    keywords='trac plugin',

    packages=find_packages(exclude=['*.tests*']),
    package_data={'tracspamfilter': [
        'templates/*',
        'htdocs/*',
        'fonts/*',
        'locale/*/LC_MESSAGES/*.mo'
    ]},
    install_requires=['Trac'],
    extras_require={
        'dns': ['dnspython>=1.3.5'],
        'spambayes': ['spambayes'],
        'pillow': ['pillow>=2'],
        'account': ['TracAccountManager >= 0.4'],
        'oauth': ['oauth2'],
        'httplib2': ['httplib2']
    },
    entry_points="""
        [trac.plugins]
        spamfilter = tracspamfilter.api
        spamfilter.filtersystem = tracspamfilter.filtersystem
        spamfilter.admin = tracspamfilter.admin
        spamfilter.adminusers = tracspamfilter.adminusers
        spamfilter.adminreport = tracspamfilter.adminreport
        spamfilter.adapters = tracspamfilter.adapters
        spamfilter.report = tracspamfilter.report
        spamfilter.accountadapter = tracspamfilter.accountadapter[account]
        spamfilter.registration = tracspamfilter.filters.registration[account]
        spamfilter.akismet = tracspamfilter.filters.akismet
        spamfilter.stopforumspam = tracspamfilter.filters.stopforumspam
        spamfilter.botscout = tracspamfilter.filters.botscout
        spamfilter.fspamlist = tracspamfilter.filters.fspamlist
        spamfilter.blogspam = tracspamfilter.filters.blogspam
        spamfilter.mollom = tracspamfilter.filters.mollom[oauth,httplib2]
        spamfilter.bayes = tracspamfilter.filters.bayes[spambayes]
        spamfilter.extlinks = tracspamfilter.filters.extlinks
        spamfilter.httpbl = tracspamfilter.filters.httpbl[dns]
        spamfilter.ip_blacklist = tracspamfilter.filters.ip_blacklist[dns]
        spamfilter.url_blacklist = tracspamfilter.filters.url_blacklist[dns]
        spamfilter.ip_throttle = tracspamfilter.filters.ip_throttle
        spamfilter.regex = tracspamfilter.filters.regex
        spamfilter.trapfield = tracspamfilter.filters.trapfield
        spamfilter.ip_regex = tracspamfilter.filters.ip_regex
        spamfilter.session = tracspamfilter.filters.session
        spamfilter.captcha = tracspamfilter.captcha.api
        spamfilter.captcha.admin = tracspamfilter.captcha.admin
        spamfilter.captcha.image = tracspamfilter.captcha.image[pillow]
        spamfilter.captcha.expression = tracspamfilter.captcha.expression
        spamfilter.captcha.rand = tracspamfilter.captcha.rand
        spamfilter.captcha.recaptcha2 = tracspamfilter.captcha.recaptcha2
        spamfilter.captcha.keycaptcha = tracspamfilter.captcha.keycaptcha
        spamfilter.captcha.mollom = tracspamfilter.captcha.mollom[oauth,httplib2]
    """,
    test_suite='tracspamfilter.tests.test_suite',
    zip_safe=False,
    **extra
)
