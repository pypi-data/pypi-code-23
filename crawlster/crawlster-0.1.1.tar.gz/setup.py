from setuptools import find_packages, setup
import os.path


def requirements(*req_files):
    items = set()
    for filename in req_files:
        file_path = os.path.join('requirements', filename)
        with open(file_path) as f:
            items |= {i.strip() for i in f.readlines() if
                      not i.startswith('-r') and not i.endswith('.txt')}
    return list(items)


setup(
    name="crawlster",
    version="0.1.1",

    description="None",
    long_description="None",
    license='MIT',

    include_package_data=True,
    packages=find_packages(),
    install_requires=requirements('base.txt'),
    extras_require={
        'advanced': [
            'lxml'
        ]
    },

    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
    ]
)
