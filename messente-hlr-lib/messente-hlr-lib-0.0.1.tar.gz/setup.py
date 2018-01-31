# -*- coding: utf-8 -*-

from setuptools import setup

setup(
    name="messente-hlr-lib",
    version="0.0.1",
    packages=[
        "messente_hlr",
    ],
    install_requires=["requests==2.18.4"],
    tests_require=["requests-mock==1.3.0", "mock==2.0.0"],
    author="messente",
    author_email="support@messente.com",
    description="Hlr api library",
    keywords="HLR api library",
    test_suite="messente_hlr.test"
)
