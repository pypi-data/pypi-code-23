import pyconrad.autoinit
import numpy as np
import pyopencl as cl

ctx = pyconrad.opencl.get_conrad_context()
queue = pyconrad.opencl.get_conrad_command_queue()
prg = cl.Program(ctx, """
__kernel void doubleIt(
    __global float *array)
{
    int gid = get_global_id(0);
    array[gid] *= 2.f;
}
""").build()

random = np.random.randn(10, 20)
cl_grid = pyconrad.opencl.opencl_namespaces.OpenCLGrid2D.from_numpy(random)
array = cl_grid.as_clarray()

# on device
prg.doubleIt(queue, [array.size], None, array.data)

# on host
random *= 2

assert np.allclose(cl_grid.download_numpy(), random)
