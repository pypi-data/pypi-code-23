
SETUP_INFO = dict(
    name = 'infi.app_repo',
    version = '1.1',
    author = 'Arnon Yaari',
    author_email = 'arnony@infinidat.com',

    url = 'https://github.com/Infinidat/infi.app_repo',
    license = 'BSD',
    description = """A user-friendly RPM/DEP repository""",
    long_description = """A user-friendly RPM/DEB repository""",

    # http://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers = [
        "Intended Audience :: Developers",
        "Intended Audience :: System Administrators",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],

    install_requires = [
'docopt>=0.6.2',
'Flask-AutoIndex>=0.6',
'Flask-Cors>=3.0.3',
'Flask>=0.12.2',
'gevent>=1.2.1',
'httpie>=0.9.9',
'infi.docopt-completion>=0.2.8',
'infi.execute>=0.1.7',
'infi.gevent-utils>=0.2.3',
'infi.logging>=0.4.7',
'infi.pyutils>=1.1.3',
'infi.rpc>=0.2.5',
'infi.traceback>=0.3.15',
'ipython<6',
'pyftpdlib>=1.5.3',
'Pygments>=2.2.0',
'pysendfile>=2.0.1',
'python-dateutil>=2.6.1',
'requests>=2.18.4',
'schematics>=1.1.0.1',
'setuptools',
'waiting>=1.4.1',
'zc.buildout'
],
    namespace_packages = ['infi'],

    package_dir = {'': 'src'},
    package_data = {'': [
'*.css',
'*.html',
'*.ico',
'*.js',
'*.mako',
'*.png',
'*.sh',
'gpg_batch_file',
'nginx.conf',
'vsftpd.conf'
]},
    include_package_data = True,
    zip_safe = False,

    entry_points = dict(
        console_scripts = [
'app_repo = infi.app_repo.scripts:app_repo',
'eapp_repo = infi.app_repo.scripts:eapp_repo'
],
        gui_scripts = [],
        ),
)

if SETUP_INFO['url'] is None:
    _ = SETUP_INFO.pop('url')

def setup():
    from setuptools import setup as _setup
    from setuptools import find_packages
    SETUP_INFO['packages'] = find_packages('src')
    _setup(**SETUP_INFO)

if __name__ == '__main__':
    setup()

