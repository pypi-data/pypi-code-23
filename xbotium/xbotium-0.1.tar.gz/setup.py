from setuptools import setup


setup(name='xbotium',
    version='0.1',
    description='this is a prototype',
    long_description='Really, the cool package.',
    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.5',
        'Topic :: Text Processing :: Linguistic',
      ],
    url='http://github.com/botium/xbotium',
    author='Sentino',
    author_email='hi@sentino.org',
    license='MIT',
    packages=['xbotium'],
    install_requires=['markdown'],

    test_suite='nose.collector',
    tests_require=['nose'],
    #dependency_links=['http://github.com/user/repo/tarball/master#egg=package-1.0']
    
    zip_safe=False)