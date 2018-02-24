# -*- coding: utf-8 -*-
# This file is a part of the AnyBlok / Attachment project
#
#    Copyright (C) 2017 Jean-Sebastien SUZANNE <jssuzanne@anybox.fr>
#
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file,You can
# obtain one at http://mozilla.org/MPL/2.0/.
from setuptools import setup, find_packages
import os

version = '1.0.2'


here = os.path.abspath(os.path.dirname(__file__))

with open(os.path.join(here, 'README.rst'), 'r',
          encoding='utf-8') as readme_file:
    readme = readme_file.read()

with open(
    os.path.join(here, 'doc', 'CHANGES.rst'), 'r', encoding='utf-8'
) as change:
    CHANGES = change.read()

with open(
    os.path.join(here, 'doc', 'FRONT.rst'), 'r', encoding='utf-8'
) as front:
    FRONT = front.read()

anyblok_init = [
]

requirements = [
    'anyblok',
]

setup(
    name='anyblok_attachment',
    version=version,
    description="Versionned attachment for AnyBlok",
    long_description=readme + '\n' + FRONT + '\n' + CHANGES,
    author="jssuzanne",
    author_email='jssuzanne@anybox.fr',
    url="http://docs.anyblok-attachment.anyblok.org/%s" % version,
    packages=find_packages(),
    entry_points={
        'anyblok.init': [
            'wkhtml2pdf_config=anyblok_attachment:anyblok_init_config',
        ],
        'bloks': [
            'attachment=anyblok_attachment.bloks.attachment:AttachmentBlok',
            'report=anyblok_attachment.bloks.report:ReportBlok',
            'wkhtml2pdf=anyblok_attachment.bloks.wkhtml2pdf:WkHtml2PdfBlok',
            'report-format=anyblok_attachment.bloks.format:ReportBlok',
        ],
        'test_bloks': [
            'test_report_1=anyblok_attachment.test_bloks.test1:TestBlok',
            'test_report_2=anyblok_attachment.test_bloks.test2:TestBlok',
            'test_report_3=anyblok_attachment.test_bloks.test3:TestBlok',
        ],
    },
    include_package_data=True,
    install_requires=requirements,
    zip_safe=False,
    keywords='attachment',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
    ],
    test_suite='tests',
    tests_require=requirements + ['nose'],
)
