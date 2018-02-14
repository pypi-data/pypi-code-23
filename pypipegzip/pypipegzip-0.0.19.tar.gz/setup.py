import setuptools

setuptools.setup(
    name='pypipegzip',
    version='0.0.19',
    description='faster read of gzip files using a pipe to zcat(1)',
    long_description='pypipegzip helps you read gzipped files faster by using a subprocess',
    url='https://veltzer.github.io/pypipegzip',
    download_url='https://github.com/veltzer/pypipegzip',
    author='Mark Veltzer',
    author_email='mark.veltzer@gmail.com',
    maintainer='Mark Veltzer',
    maintainer_email='mark.veltzer@gmail.com',
    license='MIT',
    platforms=['python'],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 2',
    ],
    keywords='pipe pipeline gzip read speed pypipegzip',
    packages=setuptools.find_packages(),
)
