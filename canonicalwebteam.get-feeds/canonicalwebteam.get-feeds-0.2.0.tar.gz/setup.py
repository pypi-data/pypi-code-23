from setuptools import setup

setup(
    name='canonicalwebteam.get-feeds',
    version='0.2.0',
    author='Canonical Webteam',
    url='https://github.com/canonical-webteam/get-feeds',
    packages=[
        'canonicalwebteam',
        'canonicalwebteam.get_feeds'
    ],
    description=(
        'Functions and template tags for retrieving JSON '
        'or RSS feed content.'
    ),
    extras_require={
        'prometheus':  ["prometheus-client >= 0.1.1"],
    },
    install_requires=[
        "Django >= 1.3",
        "requests-cache >= 0.4.0",
    ],
)
