# Copyright 2018 reinforce.io. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ==============================================================================

from setuptools import setup, find_packages
import os
from tensorforce_client import __version__


setup(
    name='tensorforce-client',
    version=__version__,
    packages=find_packages(exclude=['docs', 'examples', 'docker']),
    url='https://github.com/reinforceio/tensorforce-client',
    license='Apache',
    author='Reinforce.io & ducandu research',
    author_email='sven.mika@ducandu.com',
    description='A client to run experiments in the cloud using the TensorForce reinforcement learning library.',
    keywords='Reinforcement Learning, Cloud based RL, TensorForce, TensorFlow, Unreal Engine 4, '
             'Cloud Machine Learning with GPUs',
    entry_points={
        'console_scripts': [
            'tfcli2 = tensorforce_client.tfcli:main'
        ]
    }
)

