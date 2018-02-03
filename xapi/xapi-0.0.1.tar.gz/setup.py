from setuptools import setup, find_packages

readme = 'README.md'

with open(readme, 'rb') as f:
    long_description = f.read().decode('utf-8')

setup(
    name='xapi',
    version='0.0.1',
    author='sai',
    author_email='3030159@qq.com',
    url='https://github.com/atuple/xapi',
    keywords='django, rest, api',
    description=u'django-xapi',
    license='MIT',
    packages=["xapi", "xapi.static", "xapi.static.xapi", "xapi.static.xapi.css", "xapi.static.xapi.js", "xapi.static.xapi.fonts",
              "xapi.templates", "xapi.views", ],
    zip_safe=False,
    install_requires=[
        "requests>=2.4.3",
        "python-dateutil>=2.5.2"
    ]
)
