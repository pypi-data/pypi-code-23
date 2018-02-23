
import warnings
import pytest
import os


# import pyconrad.autoinit
try:
    from pyconrad.opencl import *
    import pyconrad
    if not pyconrad.is_initialized():
        # pyconrad.setup_pyconrad(dev_dirs=['/home/stephan/projects/CONRAD'])
        pyconrad.setup_pyconrad()

except Exception as e:
    warnings.warn(str(e))
import numpy as np
import jpype

_ = pyconrad.ClassGetter('edu.stanford.rsl.tutorial.cone')


@pytest.mark.skipif("WITH_OPENCL" in os.environ and os.environ["WITH_OPENCL"] == "0", reason="Skipping this test on Travis CI.")
def test_init_cone_beam_backprojector():
    """
    CONRAD crashes on the creation of a OpenCL when using the CONRAD.jar version 1.0.7 on Linux
    (Not only in pyconrad but also when executing the only jar).
    This does not happen if you compile CONRAD from the repository
    """
    _.ConeBeamBackprojector()


@pytest.mark.skipif("WITH_OPENCL" in os.environ and os.environ["WITH_OPENCL"] == "0", reason="Skipping this test on Travis CI.")
def test_get_conrad_cl():
    print(pyconrad.opencl.get_conrad_context())
    print(pyconrad.opencl.get_conrad_command_queue())
    print(pyconrad.opencl.get_conrad_device())


# def test_pyopenclgrid():
#     ocl_grid = PyOpenClGrid(np.ndarray([10, 10], np.float32))
#
#     print(ocl_grid)
#
#     ctx = ocl_grid.context
#     queue = cl.CommandQueue(ctx)


@pytest.mark.skipif("WITH_OPENCL" in os.environ and os.environ["WITH_OPENCL"] == "0", reason="Skipping this test on Travis CI.")
def test_clgrid_classgetter():

    _.OpenCLGrid1D(_.Grid1D(20))
    _.OpenCLGrid2D(_.Grid2D(20, 20))
    _.OpenCLGrid3D(_.Grid3D(20, 20, 40))


@pytest.mark.skipif("WITH_OPENCL" in os.environ and os.environ["WITH_OPENCL"] == "0", reason="Skipping this test on Travis CI.")
def test_add_noise():
    import pyopencl.clrandom

    grid1d = _.OpenCLGrid1D(_.Grid1D(20))

    random = pyopencl.array.Array(
        pyconrad.opencl.get_conrad_command_queue(), grid1d.shape, np.float32)
    pyopencl.clrandom.fill_rand(random)
    noisy_grid1d = grid1d.as_clarray() + random

    print(grid1d)
    print(noisy_grid1d)


@pytest.mark.skipif("WITH_OPENCL" in os.environ and os.environ["WITH_OPENCL"] == "0", reason="Skipping this test on Travis CI.")
def test_clgrid_form_size():

    _.OpenCLGrid1D.from_size([20])
    _.OpenCLGrid2D.from_size([20, 30])
    _.OpenCLGrid3D.from_size([20, 30, 40])


@pytest.mark.skipif("WITH_OPENCL" in os.environ and os.environ["WITH_OPENCL"] == "0", reason="Skipping this test on Travis CI.")
def test_clgrid_form_shape():

    _.OpenCLGrid1D.from_shape([20])
    _.OpenCLGrid2D.from_shape([20, 30])
    _.OpenCLGrid3D.from_shape([20, 30, 40])


@pytest.mark.skipif("WITH_OPENCL" in os.environ and os.environ["WITH_OPENCL"] == "0", reason="Skipping this test on Travis CI.")
def test_clgrid_fromnumpy():

    random = np.random.randn(10, 20)
    cl_grid = opencl_namespaces.OpenCLGrid2D.from_numpy(random)
    print(cl_grid[2, 4])
    assert np.allclose(cl_grid[2, 4], random[4, 2])


@pytest.mark.skipif("WITH_OPENCL" in os.environ and os.environ["WITH_OPENCL"] == "0", reason="Skipping this test on Travis CI.")
def test_device_info():

    device = pyconrad.opencl.get_conrad_device()
    print(device.name)
    print(device.version)


@pytest.mark.skipif("WITH_OPENCL" in os.environ and os.environ["WITH_OPENCL"] == "0", reason="Skipping this test on Travis CI.")
def test_clgrid_upload():

    random = np.random.randn(10, 20, 30)
    oclgrid = _.OpenCLGrid1D.form_size(*reversed(random.shape))
    oclgrid.upload_numpy(random)

    print(oclgrid[2, 4])
    assert np.allclose(oclgrid[2, 4], random[4, 2])

    downloaded = oclgrid.download_numpy()
    assert np.allclose(downloaded, random)


@pytest.mark.skipif("WITH_OPENCL" in os.environ and os.environ["WITH_OPENCL"] == "0", reason="Skipping this test on Travis CI.")
def test_clgrid_upload():

    random = np.random.randn(10, 20)
    cl_grid = opencl_namespaces.OpenCLGrid2D.from_numpy(random)
    print(cl_grid[2, 4])


@pytest.mark.skipif("WITH_OPENCL" in os.environ and os.environ["WITH_OPENCL"] == "0", reason="Skipping this test on Travis CI.")
def test_clgrid_as_clarray():

    random = np.random.randn(10, 20)
    cl_grid = opencl_namespaces.OpenCLGrid2D.from_numpy(random)
    array = cl_grid.as_clarray()

    # on device
    array *= 2

    # on host
    random *= 2

    assert np.allclose(cl_grid.download_numpy(), random)


@pytest.mark.skipif("WITH_OPENCL" in os.environ and os.environ["WITH_OPENCL"] == "0", reason="Skipping this test on Travis CI.")
def test_pyopencl_kernel_on_openclgrid():

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
    cl_grid = opencl_namespaces.OpenCLGrid2D.from_numpy(random)
    array = cl_grid.as_clarray()

    # on device
    prg.doubleIt(queue, [array.size], None, array.data)

    # on host
    random *= 2

    assert np.allclose(cl_grid.download_numpy(), random)


@pytest.mark.skipif("WITH_OPENCL" in os.environ and os.environ["WITH_OPENCL"] == "0", reason="Skipping this test on Travis CI.")
def test_clgrid_as_clbuffer():

    random = np.random.randn(10, 20)
    cl_grid = opencl_namespaces.OpenCLGrid2D.from_numpy(random)
    buffer = cl_grid.as_clbuffer


# def test_creation_java_clbuffer():
#     ctx = pyconrad.opencl.get_conrad_context()
#     clarray = cl.array.Array(ctx, (10,), np.float32)
#     val = jpype.JClass('com.jogamp.opencl.CLMemory$Mem').READ_WRITE.CONFIG
#     # protected CLBuffer(final CLContext context, final long size, final long id, final int flags) {
#     foo = _.OpenCLGrid1D(_.Grid1D(10))
#     print(foo.ID)
#     java_clarray = jpype.JPackage('com').jogamp.opencl.CLBuffer(pyconrad.opencl.opencl_namespaces.OpenCLUtil.getStaticContext(), clarray.size, clarray.data.int_ptr, val)
#     # object = foo.getFoo()
#     # print(type(object))
#     print(java_clarray)

@pytest.mark.skipif("WITH_OPENCL" in os.environ and os.environ["WITH_OPENCL"] == "0", reason="Skipping this test on Travis CI.")
def test_javacl_from_pycl():
    random = np.random.randn(10, 20).astype(np.float32)

    clarray = cl.array.to_device(
        pyconrad.opencl.get_conrad_command_queue(), random)
    java = _.OpenCLGrid2D.from_clarray(clarray)
    out = java.download_numpy()

    assert np.allclose(out, random)

    out2 = java.as_numpy()
    assert np.allclose(out2, random)


if __name__ == "__main__":
    # test_device_info()
    # test_pyopencl_kernel_on_openclgrid()
    test_javacl_from_pycl()
    # test_init_cone_beam_backprojector()
    # test_get_conrad_cl()
    # test_pyopenclgrid()
    # test_add_noise()
