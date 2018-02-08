from setuptools import setup


setup(
    name='Douwa-Meta',
    version='0.0.5',
    license='MIT',
    author='jjq',
    author_email='woshijiangjinqi@163.com',
    description=u'一个flask插件,meta,type的生成预校验',
    long_description=__doc__,
    packages=['douwa_meta'],
    zip_safe=False,
    include_package_data=True,
    platforms='any',
    install_requires=[],
    classifiers=[
        'Framework :: Flask',
        'Natural Language :: English',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ]
)
