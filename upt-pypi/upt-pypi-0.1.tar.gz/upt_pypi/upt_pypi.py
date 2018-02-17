# Copyright 2018      Cyril Roelandt
#
# Licensed under the 3-clause BSD license. See the LICENSE file.
import json
import tempfile
from urllib.request import urlretrieve
import zipfile

import requests
import upt


class PyPIPackage(upt.Package):
    pass


class PyPIFrontend(upt.Frontend):
    name = 'pypi'

    @staticmethod
    def compute_requirements_from_metadata_json(json_file):
        requirements = {}

        def _to_pkg_reqs(l):
            out = []
            for s in l:
                try:
                    name, specifier = s.split()
                    specifier = specifier[1:-1]  # Remove parentheses
                except ValueError:
                    name = s
                    specifier = None
                out.append(upt.PackageRequirement(name, specifier))

            return out

        try:
            with open(json_file) as f:
                j = json.load(f)
                for reqs in j.get('run_requires', []):
                    if 'extra' in reqs:
                        continue
                    requirements['run'] = _to_pkg_reqs(reqs['requires'])
                for reqs in j.get('test_requires', []):
                    if 'extra' in reqs:
                        continue
                    requirements['test'] = _to_pkg_reqs(reqs['requires'])
        except json.JSONDecodeError:
            return {}

        return requirements

    def compute_requirements_from_wheel(self, wheel_url):
        with tempfile.NamedTemporaryFile() as wheel,\
             tempfile.TemporaryDirectory() as d:
            urlretrieve(wheel_url, wheel.name)
            dirname = '-'.join(wheel_url.rsplit('/', 1)[-1].split('-', 2)[:2])
            dirname += '.dist-info'
            z = zipfile.ZipFile(wheel.name)
            z.extract(f'{dirname}/metadata.json', d)
            return self.compute_requirements_from_metadata_json(
                f'{d}/{dirname}/metadata.json')

    def compute_requirements(self, release):
        for elt in release:
            if elt['packagetype'] == 'bdist_wheel':
                wheel_url = elt['url']
                return self.compute_requirements_from_wheel(wheel_url)
        else:
            return {}

    def parse(self, pkg_name):
        url = f'https://pypi.org/pypi/{pkg_name}/json'
        r = requests.get(url)
        if not r.ok:
            raise upt.InvalidPackageNameError(self.name, pkg_name)
        json = r.json()
        version = json['info']['version']
        requirements = self.compute_requirements(json['releases'][version])
        d = {
            'homepage': json['info']['home_page'],
            'summary': json['info']['summary'],
            'description': json['info']['description'],
            'requirements': requirements,
        }
        return PyPIPackage(pkg_name, version, **d)
