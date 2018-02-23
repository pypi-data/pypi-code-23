import os
from setuptools import setup

if __name__ == "__main__":
    setup(
        name="vaisdemo",
        author='VAIS',
        packages=['vaisdemo'],
        package_data={'': ['vaisdemo/speech', 'vaisdemo/controller_mic.kv', 'vaisdemo/controller_video.kv']},
        author_email='support@vais.vn',
        url='https://vais.vn',
        include_package_data=True,
        install_requires=["grpcio==1.4.0", "pyyaml", "future", "docutils", "pyaudio", "pygments", "pypiwin32", "kivy.deps.sdl2", "kivy.deps.glew", "kivy"],
        version="0.1.1-a3",
        python_requires='>=2.6, !=3.0.*, !=3.1.*, !=3.2.*, <4',
    )
