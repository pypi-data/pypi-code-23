from setuptools import setup, find_packages

setup(
    name = 'APMonitor',
    version = '0.34',
    description = 'Python package to interface with the APMonitor optimization suite',
    author = 'John Hedengren',
    author_email = 'john_hedengren@byu.edu',
    url = 'https://github.com/APMonitor/apm_python', # use the URL to the github repo
    keywords='DAE optimization MILP MINLP QP NLP MIDO IPOPT',
    packages=find_packages(),
    #packages=['APMonitor'],
    classifiers=[
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
)

