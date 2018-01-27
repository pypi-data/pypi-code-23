from setuptools import setup


setup(
    name='pytest-cricri',
    description='A Cricri plugin for pytest.',
    author='Vincent Maillol',
    author_email='vincent.maillol@gmail.com',
    version='1.0',
    license='GPLv3',

    packages=['pytest_cricri'],
    entry_points={
        'pytest11': [
            'cricri = pytest_cricri.plugin',
        ]
    },
    classifiers=[
        'Framework :: Pytest',
        'Topic :: Software Development :: Testing',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
    ],
    python_requires='>=3.4',
    install_requires=['cricri', 'pytest']
)
