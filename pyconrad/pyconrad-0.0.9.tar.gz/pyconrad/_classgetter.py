import pyconrad
from jpype import JPackage
from pyconrad._pyconrad import assert_pyconrad_initialization


class ClassGetter:
    """
    Does the same thing as the old PyConrad()['Class'] but not globally,
    i.e. you can have multiple sets of namespaces (e.g. per file)
    """

    def __init__(self, *namespaces):
        self._imported_namespaces = [n for n in namespaces]
        self.edu = JPackage('edu')
        self.ij = JPackage('ij')
        self.stanfordrsl = JPackage('edu.stanford.rsl')
        self.enable_subnamespaces = False

    def add_namespaces(self, namespaces):
        if isinstance(namespaces, list):
            for e in namespaces:
                self.add_namespaces(e)
        self._imported_namespaces.append(namespaces)

    @property
    def SimpleVector(self):
        assert_pyconrad_initialization()
        return pyconrad.JClass('edu.stanford.rsl.conrad.numerics.SimpleVector')

    @property
    def PointND(self):
        assert_pyconrad_initialization()
        return pyconrad.JClass('edu.stanford.rsl.conrad.geometry.shapes.simple.PointND')

    @property
    def SimpleMatrix(self):
        assert_pyconrad_initialization()
        return pyconrad.JClass('edu.stanford.rsl.conrad.numerics.SimpleMatrix')

    @property
    def NumericGrid(self):
        assert_pyconrad_initialization()
        return pyconrad.JClass('edu.stanford.rsl.conrad.data.numeric.NumericGrid')

    @property
    def Grid1D(self):
        assert_pyconrad_initialization()
        return pyconrad.JClass('edu.stanford.rsl.conrad.data.numeric.Grid1D')

    @property
    def Grid2D(self):
        assert_pyconrad_initialization()
        return pyconrad.JClass('edu.stanford.rsl.conrad.data.numeric.Grid2D')

    @property
    def Grid3D(self):
        assert_pyconrad_initialization()
        return pyconrad.JClass('edu.stanford.rsl.conrad.data.numeric.Grid3D')

    @property
    def Grid4D(self):
        assert_pyconrad_initialization()
        return pyconrad.JClass('edu.stanford.rsl.conrad.data.numeric.Grid4D')

    @property
    def OpenCLGrid1D(self):
        assert_pyconrad_initialization()
        return pyconrad.JClass('edu.stanford.rsl.conrad.data.numeric.opencl.OpenCLGrid1D')

    @property
    def OpenCLGrid2D(self):
        assert_pyconrad_initialization()
        return pyconrad.JClass('edu.stanford.rsl.conrad.data.numeric.opencl.OpenCLGrid2D')

    @property
    def OpenCLGrid3D(self):
        assert_pyconrad_initialization()
        return pyconrad.JClass('edu.stanford.rsl.conrad.data.numeric.opencl.OpenCLGrid3D')

    # OpenCLGrid4D does not exist!

    def enumval_from_int(self, enum_name: str, value_int):
        assert_pyconrad_initialization()
        return self.__getattr__(enum_name).values()[int(value_int)]

    def enumval_from_string(self, enum_name: str, value_string: str):
        assert_pyconrad_initialization()
        return self.__getattr__(enum_name).enum_name.valueOf(value_string)

    def __getattr__(self, classname):
        assert_pyconrad_initialization()
        success = None

        # Default namespace
        try:
            rtn = pyconrad.JClass(classname)
            success = rtn
        except Exception:
            pass

        # Imported namespaces
        for package in self._imported_namespaces:
            try:
                rtn = pyconrad.JClass(package + "." + classname)
                success = rtn
                break
            except Exception:
                pass

        # Class not found? Create new ClassGetter to search in sub-namespaces
        if not success and self.enable_subnamespaces:
            if self._imported_namespaces:
                return ClassGetter(*([ns + '.' + classname for ns in self._imported_namespaces] + [classname]))

        if not success:
            raise Exception("Class \"%s\" not found in the following namespaces:\n %s" % (
                classname, self._imported_namespaces))

        return rtn

    def __getitem__(self, classname):
        if not pyconrad.is_initialized():
            raise Exception('JVM not started! Use Pyconrad().setup()')
        return self.__getattr__(classname)

    # def __call__(self):
    #     if self._imported_namespaces and self._imported_namespaces[0].contains('.'):
    #         raise Exception("Class \"%s\" not found in the following namespaces:\n %s" % (
    #             str.split(self._imported_namespaces[0], '.')[-1], ['.'.join(str.split(ns, '.')[:-1]) for ns in self._imported_namespaces]))
    #     else:
    #         raise Exception("Class not found in the following namespaces:\n %s" % (
    #             '[]'))
