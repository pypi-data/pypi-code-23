import os
import tempfile

from .utils import cypyle, build_extension, import_extension


class Cypyler:

    def __init__(self, build_dir, libraries=None, include_dirs=None):
        """ Instatiates a cypyler.
        :param build_dir: Path to the directory where the build will occur.
        :param libraries: List of libraries to pass to Cython.
        :param include_dirs: List of include directories to pass to Cython.
        :type build_dir: str
        :type libraries: list[str]
        :type include_dirs: list[str]
        """
        self.build_dir = build_dir
        self.libraries = libraries
        self.include_dirs = include_dirs

    def build(self, code, suffix='.pyx'):
        # A python module must begin with a underscore or letter, hence the prefix
        module_fd, module_path = tempfile.mkstemp(
            prefix='_', suffix=suffix, dir=self.build_dir)

        module_filename = os.path.basename(module_path)
        module_name = os.path.splitext(module_filename)[0]

        with os.fdopen(module_fd, 'w') as f:
            f.write(code)

        extensions = cypyle(module_name, module_path,
                            include_dirs=self.include_dirs,
                            libraries=self.libraries)

        built_ext = build_extension(extensions[0], self.build_dir)
        ext_path = built_ext.get_ext_fullpath(module_name)

        built_module = import_extension(module_name, ext_path)

        return built_module


class TMPCypyler(Cypyler):

    def __init__(self, build_dir_prefix='', libraries=None, include_dirs=None):
        """ Instatiates a cypyler that uses a temporary directory as build dir.
        :param build_dir_prefix: Prefix to the build directory.
        :param libraries: List of libraries to pass to Cython.
        :param include_dirs: List of include directories to pass to Cython.
        :type build_dir_prefix: str
        :type libraries: list[str]
        :type include_dirs: list[str]
        """
        build_dir = tempfile.mkdtemp(prefix=build_dir_prefix)

        super().__init__(build_dir, libraries, include_dirs)
