from setuptools import setup

setup(
    name='jupyterhub-ldapauthenticator-latest',
    version='1.2',
    description='LDAP Authenticator for JupyterHub',
    url='https://github.com/yuvipanda/ldapauthenticator',
    author='Yuvi Panda',
    author_email='yuvipanda@riseup.net',
    license='3 Clause BSD',
    packages=['ldapauthenticator'],
    install_requires=[
        'ldap3',
        'jupyterhub',
    ]
)
