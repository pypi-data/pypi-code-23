#!/usr/bin/env python
"""showslice v%s
Usage:
  showslice [options] <binfile>

Arguments:
  <binfile>  : data file

Options:
  -v, --version  : print version number and exit.
  -h, --help     : print this help mesasge and exit.
  --log=<lvl>  : CRITICAL|WARN(ING)|[default: INFO]|DEBUG|NOTSET
  --parfile=<p>    : (default: <binfile>.rstrip('_1.bin') + '.par')
  --vmax=<v>   : [default: auto]|each_auto|none|<float>
  --vmin=<v>   : [default: auto]|each_auto|none|<float>
  -n=<N>       : int, slice number (default: half way)
  --medfilt=<m>    : int, median filter size [default: 1] is off
  --srmip=<D>  : int, Short-range MIP half-width depth [default: 0]
                 ignored for `--d3`
  --dpi=<D>    : int, [default: 120] for 860 x 540 px figsize
  --out=<dir>  : [default: out]
  --save       : bool, whether to save npz/mat
  --downscale  : bool, whether to downscale by `medfilt` before saving
  --d3  : bool, do 3D projection and use `n` as polar angle in degrees
  --d4  : bool, do both with and without `--d3`

%s
"""
from __future__ import division

import matplotlib
matplotlib.use("TkAgg")  # NOQA
from matplotlib.backends.backend_tkagg import \
    FigureCanvasTkAgg, NavigationToolbar2TkAgg
# from matplotlib.figure import Figure
import matplotlib.pyplot as plt
try:
  # Python 3
  import tkinter as tk
  from tkinter import ttk
except ImportError:
  # Python 2
  import Tkinter as tk
  import Tkinter as ttk

import logging
from docopt import docopt
from argopt import DictAttrWrap
from tqdm import tqdm, trange
import numpy as np
import re
import os
from ..utils import memoise

__version__ = "1.0.1"
__author__ = "Casper da Costa-Luis <casper.dcl@physics.org>"


RE_PARAMS = re.compile(r"^(\w+)\s+\:\s+(.+)$", flags=re.M)
RE_VALUES = re.compile(
    r'^([0-9]+)\s+(\w+\s+)?"([-\w\s]+)"(\s*right\s*|\s*left\s*)?$', flags=re.M)


def stripEnd(s, ext):
  """Usage:
  >>> stripEnd("some..ext", ".ext")
  "some."
  """
  return s[:-len(ext)] if s.endswith(ext) else s


def params(parfile):
  log = logging.getLogger(__name__)
  res = dict()
  with open(parfile) as fn:
    raw = fn.read()

    reRes = RE_PARAMS.findall(raw)
    log.debug(reRes)
    res.update([(k.split('(', 1)[0].rstrip('; \t'), v) for (v, k) in reRes])

    reVals = RE_VALUES.findall(raw)
    log.debug(reVals)
    vals = set([int(i[0]) for i in reVals])
    log.debug(vals)
    res["vmax"] = max(vals)
    res["vmin"] = min(vals)

  log.debug(res)
  return res


@memoise()
def knlRotate(D, H, W):
  from caspyr.cuda import CudaFunc3D
  knl = CudaFunc3D([W, H, 1], block_dim=[16, 16, 1])
  knl.build("""
  ( float dst[][N_DIM_Y][N_DIM_X]
  , float src[][N_DIM_Y][N_DIM_X]
  , float ang)
  {
    unsigned x = blockIdx.x * B_DIM_X + threadIdx.x;
    if (x >= N_DIM_X) return;
    unsigned y = blockIdx.y * B_DIM_Y + threadIdx.y;
    if (y >= N_DIM_Y) return;
    unsigned z = blockIdx.z * B_DIM_Z + threadIdx.z;
    if (z >= N_DIM_Z) return;

    float xMid = x - N_DIM_X / 2.0f;
    float yMid = y - N_DIM_Y / 2.0f;
    float s = sin(ang);
    float c = cos(ang);

    int xx = round(N_DIM_X / 2.0f + xMid * c + yMid * s);
    if (0 > xx || xx >= N_DIM_X) return;
    int yy = round(N_DIM_Y / 2.0f - xMid * s + yMid * c);
    if (0 > yy || yy >= N_DIM_Y) return;

    for (unsigned zz = 0; zz < N_REAL_DIM_Z; ++zz)
      dst[zz][y][x] = src[zz][yy][xx];
  }""".replace("N_REAL_DIM_Z", str(D)))
  return knl


def mipRot(rotate, iproj=np.max):
  def inner(vol, iAng, axes=(2, 1), reshape=False, order=0, axis=1):
    return iproj(rotate(
        vol, iAng, axes=axes, reshape=reshape, order=order), axis=axis)
  return inner


@memoise()
def knlRotations(NAngles, D, H, W):
  from caspyr.cuda import CudaFunc3D
  knl = CudaFunc3D([W, H, NAngles], block_dim=[8, 8, 4])
  knl.build("""
  ( float dst[][N_REAL_DIM_Z][N_DIM_Y][N_DIM_X]
  , float src[][N_DIM_Y][N_DIM_X])
  {
    unsigned x = blockIdx.x * B_DIM_X + threadIdx.x;
    if (x >= N_DIM_X) return;
    unsigned y = blockIdx.y * B_DIM_Y + threadIdx.y;
    if (y >= N_DIM_Y) return;
    // z-dimension is actually rotation angle
    unsigned a = blockIdx.z * B_DIM_Z + threadIdx.z;
    if (a >= N_DIM_Z) return;
    float ang = float(a * 2 * 3.1415926535897932384626433832795 / N_DIM_Z);

    float xMid = x - N_DIM_X / 2.0f;
    float yMid = y - N_DIM_Y / 2.0f;
    float s = sin(ang);
    float c = cos(ang);

    int xx = round(N_DIM_X / 2.0f + xMid * c + yMid * s);
    if (0 > xx || xx >= N_DIM_X) return;
    int yy = round(N_DIM_Y / 2.0f - xMid * s + yMid * c);
    if (0 > yy || yy >= N_DIM_Y) return;

    for (unsigned z = 0; z < N_REAL_DIM_Z; ++z)
      dst[a][z][y][x] = src[z][yy][xx];
  }""".replace("N_REAL_DIM_Z", str(D)))
  return knl


def mipRots(rotates, iproj=np.max):
  def inner(vol, nAng, axes=(2, 1), reshape=False, order=0, axis=1):
    return [iproj(v, axis=axis) for v in rotates(
        vol, nAng, axes=axes, reshape=reshape, order=order)]
  return inner


@memoise()
def knlRotationMips(NAngles, D, H, W):
  """
  rotates along Z (D) NAngles times, MIPing each along Y (H)
  """
  from caspyr.cuda import CudaFunc3D
  knl = CudaFunc3D([W, H, NAngles], block_dim=[16, 1, 16])
  knl.build("""
  ( float dst[][N_REAL_DIM_Z][N_DIM_X]
  , float src[N_REAL_DIM_Z][N_DIM_Y][N_DIM_X])
  {
    unsigned x = blockIdx.x * B_DIM_X + threadIdx.x;
    if (x >= N_DIM_X) return;
    unsigned y = blockIdx.y * B_DIM_Y + threadIdx.y;
    if (y >= N_DIM_Y) return;
    // z-dimension is actually rotation angle
    unsigned a = blockIdx.z * B_DIM_Z + threadIdx.z;
    if (a >= N_DIM_Z) return;
    float ang = float(a * 2 * 3.1415926535897932384626433832795 / N_DIM_Z);

    float xMid = x - N_DIM_X / 2.0f;
    float yMid = y - N_DIM_Y / 2.0f;
    float s = sin(ang);
    float c = cos(ang);

    int xx = round(N_DIM_X / 2.0f + xMid * c + yMid * s);
    if (0 > xx || xx >= N_DIM_X) return;
    int yy = round(N_DIM_Y / 2.0f - xMid * s + yMid * c);
    if (0 > yy || yy >= N_DIM_Y) return;

    for (unsigned z = 0; z < N_REAL_DIM_Z; ++z)
      dst[a][z][x] = max(dst[a][z][x], src[z][yy][xx]);
  }""".replace("N_REAL_DIM_Z", str(D)))
  return knl


def rotProject(vols, stepDeg=6, warn_cpu=True, force_cpu=False,
               blocking=False):
  """
  vols   : array of 3D volumes, shape: N, Z, Y, X
  @return out  : array of array of 2D projections, shape:
      N, 360 / stepDeg, Z, X
  """
  from caspyr.multiprocessing import promise_mmap, cpu_count
  from scipy.ndimage import rotate as cpu_rotate
  log = logging.getLogger(__name__)

  nthreads = min(max(1, int(cpu_count() / 2)), len(vols))

  try:
    if force_cpu:
      raise ValueError("cpu")

    warn = [warn_cpu]

    def rotates(arr, NAng, **k):
      if mypy.ndim(arr) != 3:
        raise TypeError("expected 3Dinput")
      if k.get("axes") not in [(1, 2), (2, 1)] or k.get("reshape"):
        if warn[0]:
          raise NotImplementedError("can only roate about z without reshaping")
      im = arr.astype(np.float32).copy('C')
      log.debug("knl I/O shape:%s" % str(im.shape))
      dst = np.zeros((NAng, im.shape[0], im.shape[2]),
                     dtype=im.dtype, order='C')
      # D, H, W = arr.shape
      gRotate = knlRotationMips(NAng, *arr.shape)
      gRotate(gRotate.Out(dst), gRotate.In(im))
      # gRotate.sync()
      return dst

    # foreground GPU
    steps = int(360 / stepDeg)
    log.info("steps:%d" % steps)
    res = [rotates(vol, steps,
                   axes=(2, 1), reshape=False, order=0, axis=1)
           for vol in tqdm(vols, desc="volume", unit="rot", unit_scale=steps)]
  except Exception as e:
    if not (force_cpu and "cpu" == str(e)):
      log.warn("using CPU")
      log.warn(str(e))
    else:
      log.info("using CPU")
    res = None
  else:
    log.info("using GPU")

  if res is not None:
    return res

  # background CPU thread
  res = [
      promise_mmap(mipRot(cpu_rotate),
                   [(vol, iAng) for iAng in np.arange(0, 360, stepDeg)],
                   nthreads=nthreads)
      for vol in vols]

  if blocking:
    # main thread calculates from other end
    [None for vol in tqdm(res, desc="volume")
     for _ in tqdm(reversed(vol), desc="rotating", unit_scale=stepDeg)]
  return res


class StartPage(tk.Frame):
  def __init__(self, parent, controller):
    # log = logging.getLogger(__name__)
    tk.Frame.__init__(self, parent)

    self.args = controller.args
    self.par = controller.par

    self.f = plt.figure(1337, figsize=(8, 4.5),
                        dpi=self.args.dpi, facecolor="black")
    self.canvas = FigureCanvasTkAgg(self.f, self)
    self.canvas.show()
    self.grid_rowconfigure(0, weight=60)
    self.grid_columnconfigure(0, weight=1)
    self.canvas.get_tk_widget().grid(row=0, column=0, sticky="NSEW")
    # self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)

    container = tk.Frame(self)
    self.grid_rowconfigure(1, weight=1)
    container.grid(row=1, column=0, sticky="EW")

    if not self.args.anim:
      toolbar = NavigationToolbar2TkAgg(self.canvas, container)
      toolbar.update()
      # self.canvas._tkcanvas.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

    self.bQuit = tk.Button(container, bitmap="error", command=controller.quit)
    # container.grid_columnconfigure(0, weight=1)
    # self.bQuit.grid(row=1, column=1)
    self.bQuit.pack()

    self.container = container
    self.setDat(controller.dat)

  def setDat(self, dat):
    log = logging.getLogger(__name__)
    self.dat = dat
    args = self.args

    plotWidth = plotHeight = 1
    while plotHeight * plotWidth < len(self.dat):
      if plotWidth == plotHeight:
        plotWidth += 1
      else:
        plotHeight += 1
    self.f, axs = plt.subplots(plotHeight, plotWidth,
                               num=1337,
                               sharex=not args.d4, sharey=not args.d4)
    for (k, v) in (getattr(args, "fig_set") or {}).items():
      if k == "title":
        self.f.suptitle(v, y=1, verticalalignment="top", color="white")
      else:
        getattr(self.f, k)(v)
    try:
      self.axs = list(axs.flat)
      [(ax.clear(), ax.axis("off")) for ax in self.axs[len(self.dat):]]
      self.axs = list(axs.flat)[:len(self.dat)]
      log.info("%r axes created" % len(self.axs))
    except AttributeError:
      self.axs = [axs]

    self.len = max([len(d) for d in self.dat])
    z = self.len
    log.debug(z)
    if self.args.anim:
      z = 0
    else:
      self.scSlice = ttk.Scale(self.container, from_=0, to=z - 1,
                               resolution=1,
                               orient=ttk.HORIZONTAL,
                               sliderlength=5, length=600,
                               label="angle" if self.args.d3 else "slice",
                               command=self.showslice)
      # container.grid_rowconfigure(2, weight=1)
      # container.grid_columnconfigure(1, weight=7)
      # self.scSlice.grid(row=2, column=0)
      self.scSlice.pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)
    initSlice = self.args.n if self.args.n >= 0 else z // 2
    log.debug(initSlice)
    if not self.args.anim:
      self.scSlice.set(initSlice)

  def showslice(self, i, draw=True):
    log = logging.getLogger(__name__)
    i = int(i)
    log.debug(i)
    axs = self.axs
    args = self.args
    log.debug("vmin:%r, vmax:%r" % (args.vmin, args.vmax))

    ax_kwargs = getattr(args, "ax_set") or [{} for _ in axs]
    im_kwargs = getattr(args, "im_set") or [{} for _ in axs]
    assert len(self.dat) == len(axs)
    for (j, (vol, ax)) in enumerate(zip(self.dat, axs)):
      # log.debug("ax:%r" % j)
      for k, v in dict(cmap=getattr(args, "cmap", ["Greys_r"] * (j + 1))[j],
                       aspect="equal", origin="lower",
                       vmin=args.vmin[j],
                       vmax=args.vmax[j]).items():
        im_kwargs[j].setdefault(k, v)
      ax.clear()
      hwidth = getattr(args, "srmip", 0)  # Short Range MIP half-width
      d4mip = args.d4 and j >= len(axs) // 2
      if hwidth > 0 and not d4mip:
        if args.d3:
          log.warn("expected:srmip==0, got:%s" % hwidth)
        srmip = np.max(vol[max(0, min(len(vol) - 1, i - hwidth)):i + hwidth],
                       axis=0)
      elif hwidth and not d4mip:
        raise ValueError("expected:srmip>=0, got:%s" % hwidth)
      else:
        srmip = vol[min(len(vol) - 1, i)]
      ax.imshow(srmip, **im_kwargs[j])
      if d4mip:
        try:
          if args.full_line:
            raise IndexError
          xmin, xmax = (
              srmip[i] > im_kwargs[j]["vmax"] * .4)\
              .nonzero()[0][[0, -1]] / len(srmip[i])
          if xmax - xmin < 0.1:
            raise IndexError
        except IndexError:
          xmin, xmax = 0, 1
        ax.axhline(i, xmin=xmin, xmax=xmax)
      try:
        for k, v in ax_kwargs[j].items():
          if "label" == k:
            getattr(ax, "set_" + k)(v, color="white")
          elif "title" == k:
            ax.text(len(srmip[0]) / 2, 0, v,
                    color="white", va="top", ha="center")
          else:
            getattr(ax, "set_" + k)(v)
      except IndexError:
        if not d4mip:
          raise
      except Exception as e:
        log.warn(str(e))
      ax.axis("off")
    self.f.tight_layout(pad=0, h_pad=0)
    if draw:
      self.canvas.draw()
    else:
      fname = os.path.join(args.basename, "%04d.png" % i)
      log.debug(fname)
      self.f.savefig(fname, facecolor="black")


class mypy(object):
  """numpy-like functions for arbitrary dimesioned nester iterables"""

  @classmethod
  def ndim(cls, i):
    """Recursively considers i[0] until a scalar is found

    see also: np.ndim
    """
    log = logging.getLogger(__name__)

    if hasattr(i, "ndim"):
      return i.ndim

    try:
      return 1 + cls.ndim(i[0])
    except IndexError:
      pass
    except TypeError as e:
      if '__getitem__' not in str(e):
        raise
    return 0

  @classmethod
  def vec_reduce(cls, func, i):
    """Recursively considers i[0] until a vector is found

    see also: np.ndim
    """
    ndim = cls.ndim(i)
    if ndim <= 1:
      return func(i)
    else:
      return func([cls.vec_reduce(func, j) for j in i])

  @classmethod
  def min(cls, i):
    return cls.vec_reduce(min, i)

  @classmethod
  def max(cls, i):
    return cls.vec_reduce(max, i)


class MainApp(tk.Tk):
  def __init__(self, args, dat=None, datStep=None, *a, **k):
    log = logging.getLogger(__name__)
    tk.Tk.__init__(self, *a, **k)
    tk.Tk.wm_title(self, args.parfile)
    bname = "out"
    if args.parfile:
      bname = stripEnd(args.parfile, ".par")
    elif args.binfile:
      bname = stripEnd(args.binfile, "_1.bin")
    args.basename = os.path.join(
        os.path.dirname(bname),
        args.out if args.out is not None else "out",
        os.path.basename(bname))
    self.args = args
    if datStep is not None:
      raise log.warn("DeprecationWarning:use 4D input instead of datStep")
    if dat is not None:
      dat_ndim = mypy.ndim(dat)
      log.debug("dat:ndim:%d" % dat_ndim)
      if dat_ndim == 2:
        dat = dat.reshape((1, 1, dat.shape[0], dat.shape[1]))
      elif dat_ndim == 3:
        dat = [dat[i::datStep] for i in range(datStep)]
      elif dat_ndim == 4:
        if datStep is not None and datStep != 1:
          raise ValueError(
              "expected:datStep=1, got:%r since dat.ndim==4", datStep)
      else:
        raise ValueError(
            "expected:`dat.ndim in [2, 3, 4]`, got:%d" % dat.ndim)
      self.dat = dat
      z = len(dat[0])
      w = len(dat[0][0])
      # assert w == dat.shape[2]
      assert (datStep is None) or len(dat) == datStep
      self.par = {"array_size": w, "end_slice": z, "start_slice": 0,
                  "vmin": mypy.min(dat) if args.vmin == "auto" else -1,
                  "vmax": mypy.max(dat) if args.vmin == "auto" else -1}
      log.debug("global vmin/max")
    else:
      self.par = params(args.parfile)
      w = int(self.par["array size"])
      z = int(self.par["end_slice"]) - int(self.par["start_slice"]) + 1
      self.dat = np.fromfile(args.binfile, dtype=np.float32)
      log.info(len(self.dat))
      self.dat.resize((1, z, w, w))
      log.info(args.parfile + ':' + 'x'.join(map(str, self.dat.shape)))

    if args.medfilt > 1:
      from scipy.ndimage.filters import median_filter
      self.dat = median_filter(self.dat, size=tuple([1] + [args.medfilt] * 3))

    if "each" in getattr(args.vmin, "lower", lambda: "")():
      self.args.vmin = [np.min(d) for d in self.dat]
    self.argsAxisListCast("vmin")

    if "each" in getattr(args.vmax, "lower", lambda: "")():
      self.args.vmax = [np.max(d) for d in self.dat]
    self.argsAxisListCast("vmax")

    if ',' in  args.cmap:
      args.cmap = args.cmap.split(',')
    self.argsAxisListCast("cmap", dtype=str)

    # 2D slices -> 360 degrees 2D projections of 3D volumes
    if args.d3:
      self.dat = rotProject(self.dat)
    elif args.d4:
      self.dat.extend(rotProject(self.dat, stepDeg=360 / len(self.dat[0])))
      self.args.vmax.extend(self.args.vmax)
      self.args.vmin.extend(self.args.vmin)
      self.args.cmap.extend(self.args.cmap)

    if args.save and not args.anim:
      sdat = self.dat
      if args.downscale and args.medfilt > 1:
        from skimage.transform import downscale_local_mean
        sdat = downscale_local_mean(sdat, tuple([1] + [args.medfilt] * 3))
      log.info("save:" + args.basename + ".npz")
      np.savez_compressed(args.basename, sdat)
      log.info("save:" + args.basename + ".mat")
      # from scipy.io import savemat
      # savemat(bname, {"ph": sdat})
      from hdf5storage import write as savemat
      savemat({u"ph": np.asarray(sdat)}, '.', args.basename + ".mat",
              matlab_compatible=True, truncate_existing=True)

    container = tk.Frame(self)
    container.pack(side="top", fill="both", expand=True)
    container.grid_rowconfigure(0, weight=1)
    container.grid_columnconfigure(0, weight=1)

    self.frames = {}
    self.frames[StartPage] = StartPage(container, self)
    self.frames[StartPage].grid(row=0, column=0, sticky="nsew")
    f = self.show_frame(StartPage)
    if args.anim:
      if args.save:
        try:
          os.makedirs(args.basename)
        except:
          pass
      # silly fix moving axes
      for _ in range(10):
        f.showslice(0, draw=not args.save)
      for i in trange(f.len, unit="frame", disable=not args.save):
        f.showslice(i, draw=not args.save)
      if args.save:
        cmd = "ffmpeg -i {0}/%04d.png {0}.mp4".format(args.basename)
        log.info(cmd)
        os.system(cmd)
      f.showslice(f.len // 2)

  def argsAxisListCast(self, par, dtype=float):
    """
    par  : self.par key for "auto" (default)
    """
    log = logging.getLogger(__name__)
    val = getattr(self.args, par)
    valStr = getattr(val, "lower", lambda: "")()
    n = len(self.dat)
    if val is None or valStr == "none":
      setattr(self.args, par, [None] * n)
    elif valStr == "auto":
      setattr(self.args, par, [self.par[par]] * n)
    elif hasattr(val, "__iter__"):
      pass  # setattr(self.args, par, val)
    else:
      setattr(self.args, par, [dtype(val)] * n)
    log.info("%s:%s" % (par, getattr(self.args, par)))

  def show_frame(self, cont):
    log = logging.getLogger(__name__)
    log.debug(cont.__name__)
    frame = self.frames[cont]
    frame.tkraise()
    return frame


def run(args):
  """Non-TK version"""
  log = logging.getLogger(__name__)
  dat = np.fromfile(args.binfile, dtype=np.float32)
  par = params(args.parfile)
  w = int(par["array size"])
  z = int(par["end_slice"]) - int(par["start_slice"]) + 1
  log.info("%s:%dx%dx%d" % (args.parfile, w, w, z))
  dat = dat.reshape((z, w, w))[args.n if args.n >= 0 else z // 2]
  if args.medfilt > 1:
    from scipy.ndimage.filters import median_filter
    dat = median_filter(dat, size=args.medfilt)
  log.info("slice:" + 'x'.join(map(str, dat.shape)))
  plt.imshow(dat, cmap="jet", aspect="equal", origin="lower")
  plt.axis("off")
  plt.show()
  if args.save:
    sdat = dat
    if args.downscale and args.medfilt > 1:
      from skimage.transform import downscale_local_mean
      sdat = downscale_local_mean(sdat, tuple([args.medfilt] * 3))
    np.save(stripEnd(args.parfile, ".par"), sdat)


def main():
  args = DictAttrWrap(docopt(__doc__ % (__version__, __author__),
                             version=__version__))
  logging.basicConfig(level=getattr(logging, args.log, logging.INFO))
  log = logging.getLogger(__name__)
  if not args.parfile:
    args.parfile = stripEnd(args.binfile, '_1.bin') + '.par'
    log.info("parfile:" + args.parfile)

  args.n = int(args.n) if args.n is not None else -1
  args.medfilt = int(args.medfilt)
  args.srmip = int(args.srmip)
  args.dpi = int(args.dpi)
  # run(args)
  app = MainApp(args)
  app.mainloop()


if __name__ == "__main__":
  main()
