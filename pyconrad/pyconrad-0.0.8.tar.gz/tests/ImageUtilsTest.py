#author Bastian Bier

from pyconrad import PyConrad, ImageUtil, java_float_dtype
import numpy as np
from matplotlib import pyplot as plt


conrad = PyConrad.get_instance()
conrad.setup('8G', '1G')
#conrad.startReconstructionFilterPipeline()
# conrad.startConrad()

package = conrad.classes.stanford.rsl.conrad.data.numeric
packagePhantom = conrad.classes.stanford.rsl.tutorial.phantoms
packageConfig = conrad.classes.stanford.rsl.conrad.utils


gridTest = package.Grid2D(30,30)
print('Print Grid2D object:',gridTest)

# TODO: Conrad has to be started such that confuguration is available. Is loaded by Conrad? Can be done Otherwise?

config = packageConfig.Configuration.getGlobalConfiguration()
print("Print CONRAD config: ",config)
#config.getGeometry();

# Create a 2D and 3D grid with CONRAD
# dimensions
w = 500
h = 300
d = 3


#TODO does not work for Grid1D because Gri1D.getBuffer() doesn't return the buffer but a copy of it
try:
    numpyIn = np.random.rand(543)
    grid1 = ImageUtil.grid_from_numpy(numpyIn.astype(java_float_dtype))
    numpyOut = ImageUtil.numpy_from_grid(grid1)
    assert np.allclose(numpyIn, numpyOut)
    print("Test Grid1D passed")
except Exception as ex:
    print("Test Grid1D failed with exception: %s" % ex)

try:
    numpyIn = np.random.rand(44,543)
    grid1 = ImageUtil.grid_from_numpy(numpyIn.astype(java_float_dtype))
    numpyOut = ImageUtil.numpy_from_grid(grid1)
    assert np.allclose(numpyIn, numpyOut)
    print("Test Grid2D passed")
except Exception as ex:
    print("Test Grid2D failed with exception:",ex)

try:
    numpyIn = np.random.rand(6,57,42)
    grid1 = ImageUtil.grid_from_numpy(numpyIn.astype(java_float_dtype))
    numpyOut = ImageUtil.numpy_from_grid(grid1)
    assert np.allclose(numpyIn, numpyOut)
    print("Test Grid3D passed")
except Exception as ex:
    print("Test Grid3D failed with exception:",ex)

try:
    numpyIn = np.random.rand(7, 6,57,42)
    grid1 = ImageUtil.grid_from_numpy(numpyIn.astype(java_float_dtype))
    numpyOut = ImageUtil.numpy_from_grid(grid1)
    assert np.allclose(numpyIn, numpyOut)
    print("Test Grid4D passed")
except Exception as ex:
    print("Test Grid4D failed with exception:",ex)

grid2 = packagePhantom.MickeyMouseGrid2D(w,h)
print(grid2)

grid2.show("Test Grid2D")


grid3 = packagePhantom.Sphere3D(w,h,d)
grid3.setSubGrid(0, grid2)
grid3.show("Test Grid3D")
ImageUtil.save_grid_as_tiff(grid3,"bsadf.tif")

plt.ion()
outputArray2 = ImageUtil.numpy_from_grid(grid2)
plt.imshow(outputArray2, interpolation='nearest')
plt.title("Array2D")
plt.draw()
plt.pause(0.001)

plt.figure()
outputArray3 = ImageUtil.numpy_from_grid(grid3)
plt.imshow(outputArray3[0,...], interpolation='nearest')
plt.title("Array 3D")
plt.draw()
plt.pause(0.001)
ImageUtil.save_numpy_as_tiff(outputArray3,"bsadfARRAY.tif")


outputGrid2 = ImageUtil.grid_from_numpy(outputArray2)
outputGrid2.show("outputGrid2D")

outputGrid3 = ImageUtil.grid_from_numpy(outputArray3)
outputGrid3.show("outputGrid3D")

#loadedGrid = ImageUtil.loadGrid3DfromTif("C:\\StanfordRepo\\CONRADRSL\\bsadf.tif")
#loadedGrid.show("Loaded Grid")

#loadedArray = ImageUtil.loadArray3DfromTif("C:\\StanfordRepo\\CONRADRSL\\bsadf.tif")
#loadedGrid.show("Loaded Grid")

#loadedGrid2 = ImageUtil.loadGrid2DfromTif("C:\\StanfordRepo\\CONRADRSL\\bsadf0000.tif")
#loadedGrid2.show("Loaded Grid2D")

print("End")

