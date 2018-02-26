# Copyright 2018      Cyril Roelandt
#
# Licensed under the 3-clause BSD license. See the LICENSE file.
import sqlite3

import upt


class OpenBSDPackage(object):
    SQLPORTS_DB = '/usr/local/share/sqlports'

    def __init__(self):
        try:
            self.conn = sqlite3.connect(self.SQLPORTS_DB)
        except sqlite3.OperationalError:
            self.conn = None

    def __enter__(self):
        return self

    def __exit__(self, *args):
        if self.conn is not None:
            self.conn.close()

    def _to_openbsd_fullpkgpath(self, name):
        if self.conn is not None:
            query = 'SELECT FULLPKGPATH FROM PORTS WHERE PKGSPEC=?'
            cursor = self.conn.execute(query, (f'{name}-*', ))
            result = cursor.fetchone()
            if result is not None:
                return result[0]

        # The database cannot be used, or we could not find the row we wanted.
        # Let's return something anyway, and let the maintainer fix this.
        return f'xxx/{name}'

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

{self._licenses()}
PERMIT_PACKAGE_CDROM = \tXXX

{self._dependencies()}

.include <bsd.port.mk>'''

    def _pkgname(self):
        raise NotImplementedError()

    def _version_info(self):
        raise NotImplementedError()

    def _distname(self):
        raise NotImplementedError()

    def _maintainer(self):
        raise NotImplementedError()

    def _licenses(self):
        """Return a comment describing the package licenses."""
        out = ''
        for license in self.upt_pkg.licenses:
            out += f'# {license.spdx_identifier}\n'

        if not out:
            out = '# TODO: check licenses'
        else:
            out = out[:-1]  # Remove trailing \n

        return out

    def _dependencies(self):
        raise NotImplementedError()

    @staticmethod
    def _normalized_openbsd_name(name):
        """Return an OpenBSD-compatible version of a package name.

        The result of this function should be the same thing as the
        fullpkgpath, but without the leading "<category>/". For instance, the
        'requests' package in Python has 'www/py-requests' as its fullpkgpath,
        and _normalized_openbsd_name('requests') should return 'py-requests'.
        """
        raise NotImplementedError()


class OpenBSDPythonPackage(OpenBSDPackage):
    def create_package(self, upt_pkg, output=None):
        super().create_package(upt_pkg, output)

    def _pkgname(self):
        openbsd_name = self._normalized_openbsd_name(self.upt_pkg.name)
        return f'{openbsd_name}-${{MODPY_EGG_VERSION}}'

    @staticmethod
    def _normalized_openbsd_name(name):
        name = name.lower()
        if name == 'py':
            return 'py-py'

        if name.startswith('python-'):
            name = name[7:]
        elif name.startswith('py-'):
            name = name[3:]
        elif name.startswith('py'):
            name = name[2:]
        return f'py-{name}'

    def _version_info(self):
        return f'MODPY_EGG_VERSION = \t{self.upt_pkg.version}'

    def _distname(self):
        return f'{self.upt_pkg.name}-${{MODPY_EGG_VERSION}}'

    def _maintainer(self):
        return f'XXX XXX <xxx@xxx.xxx>'

    def _dependencies(self):
        def _to_openbsd_fullpkgpath(req):
            openbsd_name = self._normalized_openbsd_name(req.name)
            fullpkgpath = self._to_openbsd_fullpkgpath(openbsd_name)
            return fullpkgpath

        def _format_upt_reqs(upt_reqs):
            out = ''
            reqs = [f'{_to_openbsd_fullpkgpath(req)}${{MODPY_FLAVOR}}'
                    for req in upt_reqs]
            if reqs:
                out += f'\t\t{reqs[0]}'
                for req in reqs[1:]:
                    out += f' \\\n\t\t\t{req}'
                out += '\n'
            return out

        out = ''
        for kind in ('run', 'test'):
            reqs = _format_upt_reqs(self.upt_pkg.requirements.get(kind, []))
            if reqs:
                out += f'{kind.upper()}_DEPENDS ={reqs}'
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

        with pkg_cls() as packager:
            packager.create_package(upt_pkg, output)
            print(packager.pkg_str)
