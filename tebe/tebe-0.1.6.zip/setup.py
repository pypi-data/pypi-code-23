from distutils.core import setup

setup(
    name='tebe',
    version='0.1.6',
    description='Tebe is a simple but powerful editor for Markdown and reStructuredText markup languages with Sphinx and Rst2Pdf power included',
    long_description = open("README.rst").read(),
    author='Lukasz Laba',
    author_email='lukaszlab@o2.pl',
    url='https://tebe.readthedocs.io',
    packages = [
        'tebe', 'tebe.examples', 'tebe.pycore', 'tebe.icons', 'tebe.info', 
        'tebe.gui', 'tebe.pycore.rst2pdf_conf_template', 'tebe.pycore.sphinx_conf_template', 
        'tebe.pycore.sphinx_conf_template.classic_like_web', 
        'tebe.pycore.sphinx_conf_template.basic_like_paper', 
        'tebe.pycore.sphinx_conf_template.sphinxdoc_like_web'
        ],
    package_data = {'': ['*.png', '*.rst', '*.md']},
    license = 'GNU General Public License (GPL)',
    keywords = 'sphinx, restructuredtext, markdown, markup',
    python_requires = '>2.7, <3.0',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: X11 Applications :: Qt',
        'Intended Audience :: End Users/Desktop',
        'License :: OSI Approved :: GNU General Public License (GPL)',
        'Operating System :: POSIX :: Linux',
        'Operating System :: Microsoft :: Windows',
        'Programming Language :: Python',
        'Topic :: Scientific/Engineering',
        'Topic :: Documentation :: Sphinx',
        'Topic :: Office/Business',
        'Topic :: Text Editors',
        ],
    )
