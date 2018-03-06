from __future__ import division
import pycuda.driver as cuda
import pycuda.autoinit  # NOQA
from pycuda.compiler import SourceModule
import pycuda.gpuarray as gpuarray
import numpy as np
import logging

__all__ = ["cuda", "gpuarray", "CudaFunc3D", "CudaFunc"]
__author__ = "Casper da Costa-Luis <casper.dcl@physics.org>"
__version__ = "0.0.0"


class CudaFunc3D(object):
  In = cuda.In
  Out = cuda.Out

  def __init__(self, n_dim, block_dim=None, grid_dim=None,
               size_t=np.uint32, wrapper=None):
    """PyCUDA function wrapper.
    n_dim  : 3-tuple (x, y, z) of dimensions (used in grid dim calculation)
    block_dim  : 3-tuple (x, y, z) (default: (1024, 1, 1))
    grid_dim  : 3-tuple (x, y, z) (default: (n_dim + block_dim - 1) / block_dim)
    wrapper  : 2-tuple string added around `build` code (default:(
            'extern "C" { __global__ void func', "}\n"
        ))
    """
    self.start = cuda.Event()
    self.end = cuda.Event()
    self.size_t = size_t
    self.n_dim = size_t(n_dim)
    self.size = size_t(reduce(lambda x, y: x * y, n_dim))

    if block_dim is None:
      self.block_dim = [1024] + [1] * (len(n_dim) - 1)
    else:
      self.block_dim = block_dim

    if grid_dim is None:
      self.grid_dim = [(n + b - 1) // b
                       for (n, b) in zip(n_dim, self.block_dim)]
    else:
      self.grid_dim = grid_dim

    if wrapper is None:
      self.wrapper = ['extern "C" { __global__ void func', "}\n"]
    else:
      self.wrapper = wrapper

  def build(self, code, no_extern_c=1, func='func', wrapper=None, **kwargs):
    """Compile module.
    kwargs  : passed to `SourceModule`.
    """
    log = logging.getLogger(__name__)

    define = dict(
        N_DIM_X=self.n_dim[0],
        N_DIM_Y=self.n_dim[1],
        N_DIM_Z=self.n_dim[2],
        N_DIM=sum(self.n_dim),
        B_DIM_X=self.block_dim[0],
        B_DIM_Y=self.block_dim[1],
        B_DIM_Z=self.block_dim[2]
    )
    defs = '\n'.join(map(lambda kv: "#define %s %s" % kv, define.items()))

    code = "\n{d}\n{w[0]}{c}{w[1]}".format(
        d=defs, w=wrapper or self.wrapper, c=code)
    log.debug(code)
    self.func = SourceModule(
        code, no_extern_c=no_extern_c, **kwargs).get_function(func)

  def __call__(self, *a, **k):
    self.start.record()
    for (opt, val) in dict(
        block=tuple(self.block_dim),
        grid=tuple(self.grid_dim)
    ).items():
      k.setdefault(opt, val)
    res = self.func(*a, **k)
    self.end.record()
    return res

  def sync(self):
    return self.end.synchronize()

  def elapsed(self):
    return self.start.time_till(self.end) * 1e-3


class CudaFunc(CudaFunc3D):
  def __init__(self, n_dim, block_dim=1024, **k):
    super(CudaFunc, self).__init__(
        (n_dim, 1, 1),
        block_dim=(block_dim, 1, 1),
        grid_dim=((n_dim + block_dim - 1) // block_dim, 1, 1),
        **k)
