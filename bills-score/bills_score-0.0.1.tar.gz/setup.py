from setuptools import setup, find_packages
from setuptools.command.install import install as InstallCommand


def install_numpy():
    import pip
    pip.main(['install', 'numpy'])
    pip.main(['install', 'scipy'])


install_numpy()

setup(
    python_requires='>=3.4',
    name="bills_score",
    version="0.0.1",
    description="Bills Scoring",
    author="merlinsbeard",
    author_email="bjpaat@dailywarrior.ph",
    packages=['bills_scoring', 'bills_scoring.dat', ],
    include_package_data=True,
    install_requires=[
        'fire==0.1.2',
        'bcrypt==3.1.4',
        'certifi==2017.11.5',
        'chardet==3.0.4',
        'falcon==1.3.0',
        'fire==0.1.2',
        'hug==2.3.2',
        'idna==2.6',
        'numpy>=1.13.3',
        'pandas==0.21.1',
        'python-dateutil==2.6.1',
        'python-mimeparse==1.6.0',
        'pytz==2017.3',
        'requests==2.18.4',
        'scipy==1.0.0',
        'six==1.11.0',
        'SQLAlchemy==1.2.0',
        'urllib3==1.22',
        'waitress==1.1.0',
    ],
    zip_safe=False,
    entry_points={
        'console_scripts': [
            'bills_scoring=bills_scoring.win_serve:main',
            'bills_scoring_db=bills_scoring.user_schema_db:main'
            ],
    }

)
