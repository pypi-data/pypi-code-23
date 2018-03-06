import mpl_toolkits.mplot3d.axes3d as axes3d  # NOQA
import logging
__all__ = ["errorbar3d"]
__author__ = "Casper da Costa-Luis <casper.dcl@physics.org>"
__version__ = "0.1.2"


def errorbar3d(ax, x, y, z, zerr=None, yerr=None, xerr=None, **kwargs):
  """3D plots with errorbars. Inspired by
  http://mple.m-artwork.eu/home/posts/simple3dplotwith3derrorbars
  """
  log = logging.getLogger(__name__)
  plotargs = dict(kwargs)
  plotargs.setdefault("linestyle", "None")
  plotargs.setdefault("marker", 'o')
  barcolour = plotargs.pop("barcolour", 'k')
  log.debug("plotargs:" + str(plotargs))
  if any(scatteropt in plotargs for scatteropt in ("s", "depthshade")):
    log.debug("scatter")
    if plotargs["linestyle"].lower() in ("none", "", " "):
      plotargs.pop("linestyle")
    ax.scatter(x, y, zs=z, **plotargs)
  else:
    log.debug("plot")
    ax.plot(x, y, zs=z, **plotargs)
  # errorbars
  for i in range(len(x)):
    if xerr is not None and xerr[i]:
      ax.plot([x[i] + xerr[i], x[i] - xerr[i]],
              [y[i], y[i]],
              [z[i], z[i]],
              marker="_", c=barcolour)
    if yerr is not None and yerr[i]:
      ax.plot([x[i], x[i]],
              [y[i] + yerr[i], y[i] - yerr[i]],
              [z[i], z[i]],
              marker="_", c=barcolour)
    if zerr is not None and zerr[i]:
      ax.plot([x[i], x[i]],
              [y[i], y[i]],
              [z[i] + zerr[i], z[i] - zerr[i]],
              marker="_", c=barcolour)
