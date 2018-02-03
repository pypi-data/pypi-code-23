from setuptools import setup, find_packages

readme = 'README.md'

with open(readme, 'rb') as f:
    long_description = f.read().decode('utf-8')

setup(
    name='xapi',
    version='0.0.2',
    author='sai',
    author_email='3030159@qq.com',
    url='https://github.com/atuple/xapi',
    keywords='django, rest, api',
    description=u'django-xapi',
    license='MIT',
    data_files=[('xapi', ['static/css/*.css','static/js/*.js','static/fonts/*','templates/*.html'])],
    packages=["xapi","xapi.templates", "xapi.views", ],
    zip_safe=False,
    install_requires=[
        "django >= 1.11.0",
        "markdown"
    ]
)
