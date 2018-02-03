from setuptools import setup, find_packages

setup(
    name='multitech_dot_flash',
    version='0.7.1',
    description='ARM Mbed Multitech xDot and mDot flash utility',
    long_description=open('README.rst').read(),
    url='https://github.com/sensidev/multitech-dot-flash',
    author='Sensidev',
    author_email='lucian.corduneanu@sensidev.com',
    license='MIT',
    packages=find_packages(exclude=["tests*"]),
    scripts=['flashit'],
    zip_safe=False,
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Unix Shell'
    ],
)
