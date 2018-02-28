from setuptools import setup


setup_requires = [
]

install_requires = [
]

dependency_links = [
]

setup(
    name='inoon_lora_packet',
    version='1.0.0',
    description='LoRa packet parser for Ino-on, Inc.',
    author='Joonkyo Kim',
    author_email='jkkim@ino-on.com',
    packages=['inoon_lora_packet', 'inoon_lora_packet.base',
              'inoon_lora_packet.bsp', 'inoon_lora_packet.v2',
              'inoon_lora_packet.v3'],
    include_package_data=True,
    install_requires=install_requires,
    setup_requires=setup_requires,
    dependency_links=dependency_links,
    # scripts=['manage.py'],
    entry_points={
        'console_scripts': [
        ],
        "egg_info.writers": [
            "foo_bar.txt = setuptools.command.egg_info:write_arg",
        ],
    },
)
