from setuptools import setup
from setuptools.command.install import install


class BuildPackageProtos(install):
    def run(self):
        install.run(self)
        from grpc.tools import command
        command.build_package_protos('')


setup(
    name='tensorflow_serving_client',
    version='0.0.9',
    description='Python client for tensorflow serving',
    author='Triage Technologies Inc.',
    author_email='ai@triage.com',
    url='https://triage.com',
    license='MIT',
    packages=[
        'tensorflow_serving_client',
        'tensorflow_serving_client.protos',
    ],
    scripts=[
        'bin/tensorflow_serving_client',
    ],
    setup_requires=[
        'cython',
    ],
    install_requires=[
        'grpcio',
        'grpcio-tools',
        'Pillow',
    ],
    cmdclass={
        'install': BuildPackageProtos,
        'develop': BuildPackageProtos,
    },
)
