from setuptools import setup

REPO_URL = 'http://github.com/brainlamp/brainlamp-toolbox'


setup(
    author='Brain Lamp',
    author_email='brainlamp18@gmail.com',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python :: 3.6',
        'Topic :: Utilities',
    ],
    description='Toolbox for Brain Lamp project',
    zip_safe=False,
    install_requires=[
        'nltk==3.2.5'
    ],
    keywords='school, big data, machine learning, artificial inteligence',
    license='BSD',
    long_description='Check `Brain Lamp Toolbox at GitHub <{}>`_.'.format(REPO_URL),
    name='brainlamp-toolbox',
    packages=[
        'brainlamp_toolbox',
        'brainlamp_toolbox.essay'
    ],
    url=REPO_URL,
    python_requires='>=3',
    version='0.1.3'
)
