import pyopencl as cl
import pyopencl.array
import pyconrad
import numpy as np
import jpype


# from pyopencl docu:
# Interoperability with other OpenCL software

# Just about every object in pyopencl supports the following interface (here shown as an example for pyopencl.MemoryObject, from which pyopencl.Buffer and pyopencl.Image inherit):

#     pyopencl.MemoryObject.from_int_ptr()
#     pyopencl.MemoryObject.int_ptr

# This allows retrieving the C-level pointer to an OpenCL object as a Python integer, which may then be passed to other C libraries whose interfaces expose OpenCL objects. It also allows turning C-level OpenCL objects obtained from other software to be turned into the corresponding pyopencl objects.

opencl_namespaces = pyconrad.ClassGetter(
    'edu.stanford.rsl.conrad.data.numeric.opencl',
    'edu.stanford.rsl.conrad.filtering.opencl',
    'edu.stanford.rsl.conrad.opencl'
)


def get_conrad_context():
    OpenCLUtil = pyconrad.edu().stanford.rsl.conrad.opencl.OpenCLUtil
    context_java = OpenCLUtil.getStaticContext()
    return cl.Context.from_int_ptr(context_java.ID)


def get_conrad_command_queue() -> cl.CommandQueue:
    OpenCLUtil = pyconrad.edu().stanford.rsl.conrad.opencl.OpenCLUtil
    command_queue_java = OpenCLUtil.getStaticCommandQueue()
    return cl.CommandQueue.from_int_ptr(command_queue_java.ID)


def get_conrad_device():
    OpenCLUtil = pyconrad.edu().stanford.rsl.conrad.opencl.OpenCLUtil
    device_java = OpenCLUtil.getStaticCommandQueue().getDevice()
    return cl.Device.from_int_ptr(device_java.ID)


if __name__ == "__main__":
    pass
