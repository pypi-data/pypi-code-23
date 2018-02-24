from setuptools import setup, find_packages


setup(name= "sample_aditya_pingle_1", version="1.0.5",
        description = "Sample project for aditya's pip experiment.",
        long_description = "This will hold very long_description for aditya's pip experiment.",
        url = "https://github.com/adiping1",
        author = "Aditya Pingle",
        author_email = "adiping1@umbc.edu",
        license = "MIT",
        classifiers = ['Development Status :: 3 - Alpha',
                        'Intended Audience :: Developers',
                        'Topic :: Software Development :: Build Tools',
                        'License :: OSI Approved :: MIT License',
                        'Programming Language :: Python :: 2.7'],
        keywords = "sample aditya piper",
        entry_points = {
                        'console_scripts': [
                                            'sampled=sample_aditya_pingle_1:main']},
        packages = find_packages(exclude=['contrib', 'docs', 'tests']),
        install_requires = ['twine'],
        project_urls = {
                        'Bug Reports': 'https://github.com/adiping1/bugs',
                        'Funding' : 'https://github.com/adiping1/funds',
                        'Say Thanks!' : 'https://github.com/adiping1/thanks',
                        'Source' : 'https://github.com/adiping1/src'
                        }
        )
        #scripts = ['sample_aditya_pingle_1/bin/sampler'],
