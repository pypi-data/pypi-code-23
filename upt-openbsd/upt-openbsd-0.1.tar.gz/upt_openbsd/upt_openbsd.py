# Copyright 2018      Cyril Roelandt
#
# Licensed under the 3-clause BSD license. See the LICENSE file.
import upt


class OpenBSDPackage(object):
    def create_package(self, upt_pkg, output=None):
        self.upt_pkg = upt_pkg
        self.pkg_str = f'''# $OpenBSD$

COMMENT = \t\t{upt_pkg.summary}

{self._version_info()}
DISTNAME = \t\t{self._distname()}
PKGNAME = \t\t{self._pkgname()}

CATEGORIES = \t\tXXX

HOMEPAGE = \t\t{upt_pkg.homepage}

MAINTAINER = \t\t{self._maintainer()}

# XXX: License
PERMIT_PACKAGE_CDROM = \tXXX

{self._dependencies()}

.include <bsd.port.mk>'''

    def _version_info(self):
        raise NotImplementedError()

    def _distname(self):
        raise NotImplementedError()

    def _maintainer(self):
        raise NotImplementedError()

    def _dependencies(self):
        raise NotImplementedError()


class OpenBSDPythonPackage(OpenBSDPackage):
    def create_package(self, upt_pkg, output=None):
        super().create_package(upt_pkg, output)

    def _pkgname(self):
        name = self.upt_pkg.name
        if name.startswith('python-'):
            name = name[7:]
        return f'py-{name}-${{MODPY_EGG_VERSION}}'

    def _version_info(self):
        return f'MODPY_EGG_VERSION = \t{self.upt_pkg.version}'

    def _distname(self):
        return f'{self.upt_pkg.name}-${{MODPY_EGG_VERSION}}'

    def _maintainer(self):
        return f'XXX XXX <xxx@xxx.xxx>'

    def _dependencies(self):
        def _to_openbsd_pkg_name(req):
            name = req.name.lower()
            if name.startswith('python-'):
                name = name[7:]
            elif name.startswith('py-'):
                name = name[3:]
            return f'xxx/{name}${{MODPY_FLAVOR}}'

        out = ''
        run_reqs = [_to_openbsd_pkg_name(req)
                    for req in self.upt_pkg.requirements.get('run', [])]
        if run_reqs:
            out += f'RUN_DEPENDS =\t\t{run_reqs[0]}\n'
            for run_req in run_reqs[1:]:
                out += f'\t\t\t{run_req} \\\n'
            out += '\n'

        test_reqs = [_to_openbsd_pkg_name(req)
                     for req in self.upt_pkg.requirements.get('test', [])]
        if test_reqs:
            out += f'TEST_DEPENDS =\t\t{test_reqs[0]}\n'
            for test_req in test_reqs[1:]:
                out += f'\t\t\t{test_req} \\\n'
            out += '\n'

        return out


class OpenBSD(upt.Backend):
    name = 'openbsd'

    def create_package(self, upt_pkg, output=None):
        pkg_classes = {
            'pypi': OpenBSDPythonPackage,
        }

        try:
            pkg_cls = pkg_classes[upt_pkg.frontend]
        except KeyError:
            raise upt.UnhandledFrontendError(self.name, upt_pkg.frontend)

        packager = pkg_cls()
        packager.create_package(upt_pkg, output)
        print(packager.pkg_str)
