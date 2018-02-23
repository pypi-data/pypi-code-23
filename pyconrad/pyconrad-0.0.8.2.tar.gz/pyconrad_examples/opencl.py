import pyconrad.autoinit
import pyopencl.clrandom
import pyopencl.array
# import gputools

_ = pyconrad.ClassGetter(
    'edu.stanford.rsl.tutorial.phantoms',
)  # type: pyconrad.AutoCompleteConrad

pyconrad.start_gui()


# create phantom
phantom2d = _.MickeyMouseGrid2D(200, 200)

# to device
phantom_cl = _.OpenCLGrid2D(phantom2d)
phantom_cl.show("Phantom")


# get same command queue as CONRAD
queue = pyconrad.opencl.get_conrad_command_queue()

# generate noise
noise = pyopencl.array.empty_like(phantom_cl.as_clarray(), queue=queue)
random_gen = pyopencl.clrandom.ThreefryGenerator(
    pyconrad.opencl.get_conrad_context())
random_gen.fill_normal(noise, queue=queue)

# Show noise
_.OpenCLGrid2D.from_clarray(noise).show('Noise')

# Add noise to phantom_cl
phantom_array = phantom_cl.as_clarray()
phantom_array += noise
_.OpenCLGrid2D.from_clarray(phantom_array).show("Noisy phantom")

# print device info
print(pyconrad.opencl.get_conrad_context())
print(pyconrad.opencl.get_conrad_command_queue())
print(pyconrad.opencl.get_conrad_device())

device = pyconrad.opencl.get_conrad_device()
print(device.name)
print(device.version)
