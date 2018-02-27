from setuptools import setup, find_packages


setup(
    name="jeeves-deepspeech",
    version='0.1.4',
    description=('DeepSpeech STT plugin for jeeves'),
    classifiers=[
        'Development Status :: 4 - Beta',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    keywords='jeeves-deepspeech',
    author='Jon Robison',
    author_email='narfman0@gmail.com',
    license='LICENSE',
    packages=find_packages(),
    include_package_data=True,
    zip_safe=True,
    install_requires=[
        'deepspeech',
        'jeeves-pa',
    ],
    entry_points={
        'jeeves.stt': [
            'deepspeech = jeeves_deepspeech:DeepSpeechSTT',
        ],
    },
    test_suite='tests/test_jeeves_deepspeech',
)
