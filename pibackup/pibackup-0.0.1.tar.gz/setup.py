from setuptools import setup

config = {
    'name': 'pibackup',
    'version': '0.0.1',
    'author': 'p1ppo',
    'packages': ['pibackup', 'lib'],
    'include_package_data': True,
    'description': 'Scheduled cloud backup for Raspberry Pi running smart home systems like fhem or iobroker',
    # 'zip_safe': False,
    # 'py_modules': [''],
    'package_data': {'lib': ['rclone', '*.json']},
    'entry_points': {
        'console_scripts': [
            'pibackup = pibackup.tbd:main',
            'pibackup-config = pibackup.tbd:main'
        ]
    },
    # 'scripts': ['bin/bin-script'],
}

setup(**config)
