from setuptools import setup

setup(
    name='squadtradefed',
    version='1.0',
    author='Milosz Wasilewski',
    author_email='milosz.wasilewski@linaro.org',
    url='https://example.com/examplepluginpackage',
    packages=['tradefed'],
    entry_points={
        'squad_plugins': [
            'tradefed=tradefed:Tradefed',
        ]
    },
    license='AGPLv3+',
    description="SQUAD plugin that parses CTS/VTS results",
    long_description="""
    SQUAD plugin that is compatible with Linaro's test-definitions
    for CTS/VTS execution. It uses test_result.xml generated
    by tradefed shell to upade test log for failed tests
    """,
    platforms='any',
    install_requires=['squad>=0.29', 'requests']
)
