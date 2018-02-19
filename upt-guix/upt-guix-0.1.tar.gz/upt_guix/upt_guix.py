# Copyright 2018      Cyril Roelandt
#
# Licensed under the 3-clause BSD license. See the LICENSE file.
import upt


class GuixPackage(object):
    def create_package(self, upt_pkg, output=None):
        self.upt_pkg = upt_pkg
        self.guix_name = self._guix_name(upt_pkg.name)
        self.pkg_str = f"""\
(define-public "{self.guix_name}"
  (package
    (name "{self.guix_name}")
    (version "{upt_pkg.version}")
    (source {self._source()})
    (build-system {self._build_system()})
    (inputs
     `({self._inputs()}))
    (native-inputs
     `({self._native_inputs()}))
    (propagated-inputs
     `({self._propagated_inputs()}))
    (home-page "{upt_pkg.homepage}")
    (synopsis "{self._synopsis()}")
    (description "XXX")
    (license #f)))"""

    def _guix_name(self, pkg_name):
        raise NotImplementedError()

    def _build_system(self):
        raise NotImplementedError()

    def _source(self):
        raise NotImplementedError()

    def _format_inputs(self, frontend_inputs):
        inputs = []
        first = True
        # TODO: We completely dismiss the requirement specifiers. This means we
        # may not know that some of the package dependencies are actually
        # outdated in Guix.
        for requirement in frontend_inputs:
            if first:
                first = False
                spaces = ''
            else:
                spaces = ' ' * 7
            req_name = self._guix_name(requirement.name)
            inputs.append(f'{spaces}("{req_name}" ,{req_name})')
        return '\n'.join(inputs)

    def _inputs(self):
        return ''

    def _native_inputs(self):
        return self._format_inputs(self.upt_pkg.requirements.get('test', []))

    def _propagated_inputs(self):
        return self._format_inputs(self.upt_pkg.requirements.get('run', []))

    def _synopsis(self):
        synopsis = self.upt_pkg.summary
        if synopsis.endswith('.') and not synopsis.endswith('etc.'):
            synopsis = synopsis[:-1]
        if synopsis.startswith('a ') or synopsis.startswith('A '):
            synopsis = synopsis[2:]
        if synopsis.startswith('an ') or synopsis.startswith('An '):
            synopsis = synopsis[3:]
        return synopsis.capitalize()


class GuixCPANPackage(GuixPackage):
    def _guix_name(self, name):
        name = name.replace('::', '-')
        if name.startswith('perl-'):
            return name.lower()
        else:
            return f'perl-{name.lower()}'

    def _build_system(self):
        return 'perl-build-system'

    def _source(self):
        try:
            url = self.upt_pkg.download_urls[0]
        except IndexError:
            url = 'TODO'

        # TODO: compute the sha256 sum of the source and print it using the
        # nix-base32 format.
        return f"""(origin
             (method url-fetch)
             (uri "{url}")
             (sha256
              (base32
               "XXX"))))"""


class GuixPythonPackage(GuixPackage):
    def create_package(self, upt_pkg, output=None):
        super().create_package(upt_pkg, output)
        py2_name = self.guix_name.replace('python-', 'python2-')
        self.pkg_str += f'\n\n(define-public {py2_name}\n'
        self.pkg_str += f'  (package-with-python2 {self.guix_name}))'

    @staticmethod
    def _guix_name(name):
        name = name.lower()
        if name.startswith('python-'):
            return name
        else:
            return f'python-{name}'

    def _build_system(self):
        return 'python-build-system'

    def _source(self):
        # TODO: compute the sha256 sum of the source and print it using the
        # nix-base32 format.
        return f"""(origin
             (method url-fetch)
             (uri (pypi-uri "{self.upt_pkg.name}" version))
             (sha256
              (base32
               "XXX"))))"""


class Guix(upt.Backend):
    name = 'guix'

    def create_package(self, upt_pkg, output=None):
        pkg_classes = {
            'cpan': GuixCPANPackage,
            'pypi': GuixPythonPackage,
        }

        try:
            pkg_cls = pkg_classes[upt_pkg.frontend]
        except KeyError:
            raise upt.UnhandledFrontendError(self.name, upt_pkg.frontend)

        packager = pkg_cls()
        packager.create_package(upt_pkg, output)
        print(packager.pkg_str)
