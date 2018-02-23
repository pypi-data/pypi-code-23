import pyconrad
import sys
import os
from os.path import basename
import numpy as np

_ = pyconrad.ClassGetter()


def start_pyconrad(*args, **kwargs):
    pyconrad.setup_pyconrad()
    pyconrad.start_reconstruction_pipeline_gui()


def start_conrad_imagej(*args, **kwargs):
    pyconrad.setup_pyconrad()
    pyconrad.start_gui()

    for f in sys.argv[1:]:
        try:
            if os.path.isfile(f):
                if str.lower(f).endswith('.vtk'):
                    import vtk
                    from vtk.util import numpy_support as VN
                    reader = vtk.vtkStructuredPointsReader()
                    reader.SetFileName(f)
                    reader.ReadAllVectorsOn()
                    reader.ReadAllScalarsOn()
                    reader.Update()
                    data = reader.GetOutput()  # type: vtkStructuredPoints
                    shape = [*reversed(data.GetDimensions())]

                    array = True
                    counter = 0
                    # while array:
                    array = VN.vtk_to_numpy(data.GetPointData().GetAbstractArray(counter)).reshape(
                        shape)
                    pyconrad.ClassGetter().Grid1D.from_numpy(
                        array).show()

                elif str.lower(f).endswith('.np') or str.lower(f).endswith('.npz'):
                    file_object = np.load(f)
                    for key in file_object.keys():
                        numpy_array = file_object[key]
                        _.NumericGrid.from_numpy(numpy_array).show(key)

                else:
                    pyconrad.ij().IJ.openImage(
                        f).show(basename(f))

        except Exception as e:
            print(e)


if __name__ == "__main__":
    start_pyconrad()
