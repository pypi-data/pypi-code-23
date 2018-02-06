
SETUP_INFO = dict(
    name = 'infi.recipe.application_packager',
    version = '2.0.4',
    author = 'Arnon Yaari',
    author_email = 'arnony@infinidat.com',

    url = 'https://github.com/Infinidat/infi.recipe.application_packager',
    license = 'BSD',
    description = """buildout recipe for packaging projects as applications""",
    long_description = """buildout recipe for packaging projects are applications""",

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
'buildout.wheel>0.1.2',
'git-py',
'infi.execute',
'infi.os_info',
'infi.recipe.buildout_logging',
'infi.recipe.close_application',
'infi.recipe.console_scripts',
'infi.registry',
'infi.traceback',
'infi.winver',
'jinja2',
'munch',
'pystick',
'pythonpy',
'setuptools',
'zc.buildout>=2.9.2'
],
    namespace_packages = ['infi', 'infi.recipe'],

    package_dir = {'': 'src'},
    package_data = {'': [
'*.bash',
'*.inc',
'changelog.in',
'control.in',
'get-pip.py',
'main.c',
'md5sums.in',
'Microsoft.VC90.CRT.manifest-x64',
'Microsoft.VC90.CRT.manifest-x86',
'msvcp100.dll',
'msvcr100.dll',
'pkginfo.in',
'postinst.in',
'postinstall.in',
'preinst.in',
'preinstall.in',
'preremove.in',
'prerm.in',
'rcedit.exe',
'rpmspec.in',
'rules.in',
'setup.py.example',
'signtool.exe',
'silent_launcher-x64.exe',
'silent_launcher-x86.exe',
'template.wxs'
]},
    include_package_data = True,
    zip_safe = False,

    entry_points = {
        'console_scripts': [
],
        'gui_scripts': [],
        'zc.buildout': [
                        'default = infi.recipe.application_packager.auto:Recipe',
                        'build_env = infi.recipe.application_packager.embedded:BuildEnvironment',
                        'executable = infi.recipe.application_packager.embedded:Executable',
                        'static_library = infi.recipe.application_packager.embedded:StaticLibrary',
                        'msi = infi.recipe.application_packager.msi:Recipe',
                        'rpm = infi.recipe.application_packager.rpm:Recipe',
                        'deb = infi.recipe.application_packager.deb:Recipe',
                       ]
        },
    )

def setup():
    from setuptools import setup as _setup
    from setuptools import find_packages
    SETUP_INFO['packages'] = find_packages('src')
    _setup(**SETUP_INFO)

if __name__ == '__main__':
    setup()

