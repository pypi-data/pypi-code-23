# Copyright 2014-present, Apstra, Inc. All rights reserved.
#
# This source code is licensed under End User License Agreement found in the
# LICENSE file at http://www.apstra.com/eula

from setuptools import setup, find_packages
from itertools import starmap


packages = find_packages()
client_mod = packages[1]
extensions_mod = [p for p in packages if p.endswith('.extensions')][0]


def make_ext_endpoint(name, module):
    return "%s = %s.%s:plugin" % (name, extensions_mod, module)


def make_ext_list(items):
    return list(starmap(make_ext_endpoint, items))


extensions_main = [
    # (name, extension module)
    ('blueprints', 'blueprints'),
    ('hardware_types', 'hcl'),
    ('systems', 'systems'),
    ('system_agents', 'system_agents'),
    ('system_agent_profiles', 'system_agent_profiles'),
    ('packages', 'packages')
]

extensions_systems = [
    # (name, extension module)
    ('services', 'system_services')
]

extensions_design = [
    # (name, extension module)
    ('rack_types', 'rack_types'),
    ('logical_devices', 'logical_devices'),
    ('logical_device_maps', 'logical_device_maps'),
    ('design_templates', 'design_templates')
]

setup(
    name="apstra-aospy-client",
    version="0.3.0",
    author="Apstra, Inc.",
    license="Apache 2.0",
    author_email="support@apstra.com",
    url="http://www.apstra.com",
    description="Python client for AOS Server",
    packages=packages,
    entry_points={
        'aospy.client': make_ext_list(extensions_main),
        'aospy.client.systems': make_ext_list(extensions_systems),
        'aospy.client.design': make_ext_list(extensions_design),
    },
    install_requires=[
        'bidict',
        'cached_property',
        'first',
        'requests',
        'retrying',
        'six',
        'inflection'
    ]
)
