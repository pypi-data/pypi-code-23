from setuptools import setup
import exr.meta_aws
setup(
    name='exr-aws',
    version=exr.meta_aws.__version__,
    author='Peter Salnikov',
    author_email='opensource@exrny.com',
    url=exr.meta_aws.__website__,
    packages=['exr', 'exr.aws', 'exr.aws.services'],
    install_requires=['boto3'],
    license='MIT License',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Intended Audience :: System Administrators',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 3'
    ],
    keywords=['framework'],
    description='Amazon AWS boto3 helper libs.',
    long_description=open('README.rst').read()+'\n'+open('CHANGES.rst').read()
)
