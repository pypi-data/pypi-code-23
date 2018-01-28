import setuptools
import versioneer


setuptools.setup(
    name='pygments-tiger',
    version=versioneer.get_version(),
    cmdclass=versioneer.get_cmdclass(),
    description='Pygments lexer for the Tiger Language',
    url='https://github.com/lse/pygments-tiger',
    author='Gabriel Laskar',
    author_email='gabriel@lse.epita.fr',
    license='MIT',
    packages=['.'],
    install_requires=[
        'pygments',
    ],
    entry_points={
        'pygments.lexers': [
            'tiger=pygments_tiger:TigerLexer',
        ],
    },
)
