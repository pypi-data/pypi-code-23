import logging
__all__ = ["Plt"]
__author__ = "Casper da Costa-Luis <casper.dcl@physics.org>"
__version__ = "0.6.0"


class Plt(object):
  """
  Manage switching between subplots and individual figures with ease
  """
  import matplotlib.pyplot as plt
  import re
  _dims = None
  _f = 0  # current figure number (number of calls to set_dims)
  _n = 1  # current (sub) figure number (number of calls to fig)
  disable = False
  RE_NPATH = re.compile("[^A-Za-z0-9_!&()-+., ]+")

  @classmethod
  def set_dims(cls, rows=None, cols=None, fig=None):
    if cls.disable:
      return
    cls._dims = [rows, cols] if rows and cols else None
    # select previous figure if going back to figure mode,
    # else create a new figure to hold subplots
    cls._f = fig or (cls._f + 1 if cls._dims else cls._f)
    cls.plt.figure(cls._f)
    cls._n = 1

  @classmethod
  def fig(cls, n=None, **kwargs):
    if cls.disable:
      return
    if cls._dims is None:
      cls._f = cls._f + 1 if n is None else max(cls._f, n)
      cls.plt.figure(cls._f)
      cls._n = 1
    else:
      if n is None:
        n = cls._n
        cls._n += 1
      d = cls._dims + [n]
      cls.plt.subplot(*d)
    for (k, v) in kwargs.items():
      getattr(cls.plt, k)(v)

  @classmethod
  def saveax(cls, ext=".png", size=None, dpi=600):
    log = logging.getLogger(__name__)
    ax = cls.plt.gca()
    if size is not None:
      cls.plt.gcf().set_size_inches(size)
    curTitle = ax.get_title()
    log.debug("plot title: " + curTitle)
    ax.set_title("")
    opath = '_'.join(cls.RE_NPATH.sub("", curTitle).strip().split()) + ext
    log.debug("saving to " + opath)
    cls.plt.savefig(opath, dpi=dpi)
    log.debug("saved")
    ax.set_title(curTitle)

  @classmethod
  def draw(cls):
    if cls.disable:
      return
    # log = logging.getLogger(__name__)
    # cls.plt.tight_layout()
    cls.plt.draw()
    cls.saveax()

  @classmethod
  def trim(cls, im, vmin=None):
    """@return (yMin, yMax, xMin, xMax)"""
    if vmin is None:
      vmin = im.min()
    xs = (im.max(0) > vmin)
    ys = (im.max(1) > vmin)
    xMin = max(0, xs.argmax() - 5)
    yMin = max(0, ys.argmax() - 5)
    xMax = min(len(xs), len(xs) + 5 - xs[::-1].argmax())
    yMax = min(len(ys), len(ys) + 5 - ys[::-1].argmax())
    return yMin, yMax, xMin, xMax

  @classmethod
  def imshow(cls, im, xlabel=None, ylabel=None, cmap="hot", trim=True):
    if cls.disable:
      return
    log = logging.getLogger(__name__)
    vmin, vmax = im.min(), im.max()
    vmean, vstd = im.mean(), im.std()
    imDbgStr = '/'.join(["{:3.2e}"] * 4).format(vmin, vmean, vmax, vstd)
    log.debug("image min/mean/max/std" + imDbgStr)
    if log.getEffectiveLevel() <= logging.DEBUG:
      ax = cls.plt.gca()
      curTitle = ax.get_title()
      ax.set_title(curTitle + ' ' + imDbgStr)
    yMin, xMin = 0, 0
    yMax, xMax = im.shape
    if trim:
      yMin, yMax, xMin, xMax = cls.trim(im, vmin=vmin)

    cls.plt.imshow(im[yMin:yMax, xMin:xMax],
                   aspect="equal", origin="lower", cmap=cmap,
                   vmin=vmin, vmax=vmax)
    if not (xlabel or ylabel):
      cls.plt.axis("off")
    else:
      # cls.plt.axis("on")
      ax = cls.plt.gca()
      ax.tick_params(axis="both", which="both",
                     labelbottom="off", labelleft="off",
                     bottom=0, left=0, top=0, right=0)
      ax.set_frame_on(False)
      if xlabel:
        cls.plt.xlabel(xlabel)
      if ylabel:
        cls.plt.ylabel(ylabel)
    cls.draw()

  @classmethod
  def __getattr__(cls, name):
    if cls.disable:
      return
    return getattr(cls.plt, name)
