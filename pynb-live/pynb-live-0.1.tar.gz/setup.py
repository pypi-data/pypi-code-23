from setuptools import setup

setup(
    author='Alexander C. Mueller',
    author_email='mail@alexcmueller.de',
    name='pynb-live',
    python_requires=">=3.4",
    version='0.1',
    packages=['pynb_livereload', ],
    license='MIT',
    long_description=open('README.rst').read(),
    classifiers=[
        # How mature is this project? Common values are
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        'Development Status :: 3 - Alpha',

        # Indicate who your project is intended for
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        'Intended Audience :: System Administrators',

        # Pick your license as you wish (should match "license" above)
        'License :: OSI Approved :: MIT License',

        # Specify the Python versions you support here. In particular, ensure
        # that you indicate whether you support Python 2, Python 3 or both.
        'Programming Language :: Python :: 3',
    ],
    install_requires=['pynb'
                      ],
    dependency_links=[
        'git+ssh://git@github.com/dice89/python-livereload.git@c3bf04de28b1f57f04c4cac2dade76c3dcb23cad#egg=livereload'
    ],
    entry_points={
        'console_scripts': [
            'pynb-live = pynb_livereload.pynb_livereload:main'
        ]
    },
)
