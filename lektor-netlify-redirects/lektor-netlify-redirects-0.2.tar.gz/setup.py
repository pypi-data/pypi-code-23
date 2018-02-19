from setuptools import setup

setup(
    name='lektor-netlify-redirects',
    version='0.2',
    author=u'DareDoes',
    author_email='me@daredoes.work',
    url='https://daredoes.work',
    description='A basic application for redirects in netlify',
    license='MIT',
    py_modules=['lektor_netlify_redirects'],
    entry_points={
        'lektor.plugins': [
            'netlify-redirects = lektor_netlify_redirects:NetlifyRedirectsPlugin',
        ]
    }
)
