#!/usr/bin/env python
"""Plots 3d series from a csv file, including titles and colours.
Usage:
  plot3d [--help|options] <files>...

Options:
  -h, --help         Print this help and exit.
  -v, --version      Print module version number and exit.
  -a, --fix-aspect   Fix aspect ratio to be 1 [default: False].
  -d, --depthshade   Add alpha to far away points [default: False].
  -t, --timeseries   Interpret the last column of data as time,
                     plotting additional graphs.
  --colours=<wheel>  Colour wheel to use for differentiating between series
                     [default: rgbcmyk].
  --trans-mod=<t>    Custom transformation module containing `my_trans()`
                     (default: None). See `pitch_transforms` for syntax.
  -r, --right        Whether to set the origin and the right of the pitch.
                     Passed as an argument to <t>.
                     If [default: False], sets the origin at the left.
  --save-mod=<s>     Custom save module containing `my_save()`
                     (default: None). See `pitch_transforms` for syntax.
  --output-path=<p>  Directory in which to save generated figures
                     (default: None).
  --log=<lvl>        Log level CRITICAL|ERROR|WARN(ING)|[default: INFO]|DEBUG.

Arguments:
  <files>  CSV files. Can include `-` (stdin).
           Line commands begin with  "#". The second character determines
           the command:

             #%Figure title (MANDATORY)
             #@Series title (MANDATORY)
             # Comment

           3D points are specified simply as:

             1.0,2,-3.141592653589793

           Symmetric x/y/z errors may optionally be specified:

             0.5,0.6,0.3,0.25,0.3,0.15

           Series titles can be postfixed with {.options}, as follows:

             {.plot_type=scatter}  (DEFAULT: scatter)
           | {.plot_type=plot}
             {.c=colour}           (DEFAULT: auto, from --colours=<wheel>)
             {.depthshade=}        (DEFAULT: auto, from --depthshade)
           | {.depthshade=1}
             {.s=<point_size>}     (DEFAULT: 32.0)
             {.alpha=<alpha>}      (DEFAULT: 1.0)
             {.xlabel=<x>}         (DEFAULT: x)

           Errorbar options:

             {.linestyle=<s>}      (DEFAULT: : if plot_type==plot else None)
             {.marker=<m>}         (DEFAULT: o if plot_type==scatter else None)

           Figure options:

             {.projection=3d}      (DEFAULT: 3d)
           | {.projection=2d}

           Any other options are forwarded to matplotlib.

           If y and/or z are unspecifed, they are assumed zero.
           A fourth integer coordinate may be specified for indexing.
           You can create multiple figures
           (TODO: resets colour wheel index):

             #%Another figure
"""
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D  # NOQA
from ..plotting import errorbar3d
from importlib import import_module
import sys
import re
import os.path
import logging
__author__ = "Casper da Costa-Luis <casper.dcl@physics.org>"
__all__ = ["main"]
__version__ = "0.18.1"


RE_options = re.compile(r'\s*\{\.(\w+)=(.*?[^\\])\}')


def get_options(s):
  """
  >>> get_options('foo {.bar=baz} {.bat=3}')
  {'bat': '3', 'bar': 'baz'}
  """
  return dict((k, v.replace(r"\}", "}").replace(r"\ ", ""))
              for (k, v) in RE_options.findall(s))


def strip_options(s):
  """
  >>> strip_options('foo {.bar=baz} {.bat=3}')
  'foo'
  """
  return RE_options.sub('', s)


def coord(m, i):
  """
  i^{th} column of a row-major matrix m. (Equivalently,
  i^{th} row of a column-major matrix m.)

  Parameters
  ----------
  m  : list of lists
  i  : int

  Returns
  -------
  out  : list
      i^{th} element of each list in m

  Example
  -------

  >>> coord([[0, 1, 2], [4, 1, 9], [6, 1, 5]], 1)
  [1, 1, 1]
  """
  return [v[i] if (0 <= i < len(v)) else 0 for v in m]


def save_csv(series, fname='plot3d_out.csv'):
  # TODO: errors
  log = logging.getLogger()
  log.info("Saving to " + fname)
  with open(fname, 'w') as fp:
    fig_names = []
    for series_name in sorted(series.keys()):
      if series_name[2] not in fig_names:
        fig_names.append(series_name[2])
        fp.write('#%' + series_name[2] + '\n')

      fp.write('\n#@' + series_name[1] + '\n')
      fp.write('\n'.join(','.join('{0:.3f}'.format(i).replace('.000', '')
                                  for i in xyz)
                         for xyz in series[series_name]) + '\n')


def fn_prepend(f, p='', s=''):
    r"""prefix/suffix basename within a full file path
    f  : full file path
    p  : prefix
    s  : suffix (before extension, if exists)

    Example
    -------

    >>> fn_prepend('C:\\path\\to.a\\file...with_an.ext', 'foo_', '_bar')
    'C:\\path\\to.a\\foo_file...with_an_bar.ext'

    """
    ftree = list(os.path.split(f))
    basename = '.'.join(ftree[-1].split('.')[:-1])
    ext = ftree[-1].split('.')[-1] if ftree[-1].count('.') > 0 else ''
    ftree[-1] = p + basename + s + '.' + ext
    return os.path.join(*ftree)


def axisEqual3D(ax3d):
  """Sets aspect ratio == (1,1) for a 3D axis"""
  import numpy as np
  extents = np.array([getattr(ax3d, 'get_' + dim + 'lim')() for dim in 'xyz'])
  sz = extents[:, 1] - extents[:, 0]
  centres = np.mean(extents, axis=1)
  r = max(abs(sz)) / 2
  for ctr, dim in zip(centres, 'xyz'):
    getattr(ax3d, 'set_' + dim + 'lim')(ctr - r, ctr + r)


def get(l, i, default_val=None):
  """Default getter"""
  try:
    return l[i]
  except IndexError:
    return default_val
  except KeyError:
    return default_val


def main():
  from docopt import docopt
  args = docopt(__doc__, version=__version__)
  logging.basicConfig(level=getattr(logging, args["--log"]))
  log = logging.getLogger()
  log.debug(str(args))

  colours = args['--colours']
  axs = []

  for fname in args['<files>']:
    log.info("Processing:" + fname)
    series = {}  # {(ax_num, 'series_name', 'fig_name')
    #            #  : [[x0,y0,z0], ... ], ... }
    series_name = ''
    fig_name = ''
    with (sys.stdin if fname is '-' else open(fname)) as fp:
      for raw_row in fp:
        row = raw_row.strip()
        if not len(row):
          continue
        elif row[0] == '#':  # Comment
          if len(row) > 1:
            if row[1] == '@':  # Series
              series_name = row[2:]
              log.info("Found:Series:" + series_name)
              series[(len(axs), series_name, fig_name)] = []
            elif row[1] == '%':  # Figure
              fig = plt.figure()
              projection = get_options(row).get("projection", "3d").lower()
              projection = "3d" if projection == "3d" else None
              axs.append(fig.add_subplot(111, projection=projection))
              log.info("Found:Figure:" + row[2:])
              fig_name = strip_options(row[2:])
              plt.title(fig_name)
        else:
          series[(len(axs), series_name, fig_name)].append(map(
              lambda x: float(x) if x else 0.0, row.split(',')))

    while len(series) > len(colours):
      colours = colours * 2

    ofname = fn_prepend(fname, 'trans_' +
                        ('R' if args['--right'] else 'L') + '_')
    if args['--trans-mod']:
      log.warn("Applying custom transformations (%s)"
               % ("R" if args['--right'] else "L"))
      my_trans = import_module(args['--trans-mod'])
      my_trans.my_trans(series, isRight=args['--right'])
      save_csv(series, ofname)
    if args['--save-mod']:
      my_save = import_module(args['--save-mod'])
      my_save.my_save(series, ofname.replace('.csv', '.json'),
                      isRight=args['--right'])

    if args['--timeseries']:
      # private axes for components

      log.debug(str([u for v in series.values() for u in v if len(u) > 5]))

      _, _axs = plt.subplots(nrows=max(len(u)
                                       for v in series.values()
                                       for u in v) - 1,
                             ncols=1,
                             sharex=True, squeeze=True)
      plt.xlabel('time')

    for (c, series_name) in zip(colours, series.keys()):
      def p(idx):
        return coord(series[series_name], idx)
      log.info("Processing:" + series_name[1])

      ax = axs[series_name[0] - 1]
      is3d = hasattr(ax, "set_zlabel")

      ax_opts = get_options(series_name[1])

      plot_type = ax_opts.get('plot_type', 'scatter')
      # label = ax_opts.get('label', strip_options(series_name[1]))
      plot_fn = getattr(ax, plot_type)
      plot_kwargs = dict(ax_opts)
      for internalOpt in ("plot_type",):
        plot_kwargs.pop(internalOpt, None)
      xyzuvwlabs = [plot_kwargs.pop(i + "label", i) for i in "xyzuvw"]

      # defaults
      plot_kwargs.setdefault("label", strip_options(series_name[1]))
      plot_kwargs.setdefault("c", c)
      plot_kwargs.setdefault("alpha", 1)

      # special positive defaults
      if plot_type == "scatter":
        plot_kwargs.setdefault('s', 32)
        plot_kwargs['s'] = float(plot_kwargs['s'])
      elif plot_type == "plot":
        plot_kwargs.setdefault("lw", 2)
        plot_kwargs["lw"] = float(plot_kwargs["lw"])
        for unsupportedOpt in ("depthshade",):
          if plot_kwargs.pop(unsupportedOpt, None) is not None:
            log.warn("- %s ignored" % unsupportedOpt)
      elif not is3d:
        for unsupportedOpt in ("depthshade",):
          if plot_kwargs.pop(unsupportedOpt, None) is not None:
            log.warn("- %s ignored" % unsupportedOpt)

      # special negative defaults
      if plot_type not in ("plot",):
        if is3d:
          plot_kwargs.setdefault("depthshade", args['--depthshade'])
          plot_kwargs["depthshade"] = bool(plot_kwargs["depthshade"])

      if args['--timeseries']:
        # TODO: isErr = bool([u for u in series[series_name] if len(u) >= 8])
        isErr = bool([u for u in series[series_name] if len(u) >= 8])
        time_idx = 7 if isErr else min(len(v) for v in series[series_name]) - 1
        coord_indxs = [i for i in
                       range(max(len(v) for v in series[series_name]))
                       if i != time_idx]
        plot_fn(p(get(coord_indxs, 0, -1)),
                p(get(coord_indxs, 1, -1)),
                p(get(coord_indxs, 2, -1)), **plot_kwargs)

        plt.sca(_axs[0])
        plt.title(series_name[2])
        for ylab, indx, ax in zip(xyzuvwlabs, coord_indxs, _axs):
          plt.sca(ax)
          plot_fn = getattr(ax, plot_type)
          plot_fn(p(time_idx), p(indx), **plot_kwargs)
          plt.ylabel(ylab)
          plt.legend()
      else:
        isErr = bool([u for u in series[series_name] if len(u) >= 6])
        if isErr:
          log.info("+ errorbars")
          isPlt = plot_type == "plot"
          plot_kwargs.setdefault("linestyle", ":" if isPlt else "")
          plot_kwargs.setdefault("marker", "" if isPlt else "o")
          # for unsupportedOpt in ("s", "depthshade"):
          #   if plot_kwargs.pop(unsupportedOpt, None) is not None:
          #     log.warn("- %s ignored" % unsupportedOpt)
          errorbar3d(ax, *map(p, range(3)),
                     xerr=p(3), yerr=p(4), zerr=p(5), **plot_kwargs)
        else:
          log.debug(series_name[1])
          plot_fn(*map(p, range(3 if is3d else 2)), **plot_kwargs)

        for (crd, lab) in zip("xyz" if is3d else "xy", xyzuvwlabs):
          log.debug("labels: " + str(xyzuvwlabs))
          getattr(ax, "set_" + crd + "label")(lab)

    for ax in axs:
      plt.sca(ax)
      if args['--fix-aspect']:
        axisEqual3D(ax)
      plt.legend()
      if args['--output-path']:
        ofname = args['--output-path'].rstrip('\\/') + \
            '/' + plt.getp(ax, 'title') + '.png'
        plt.savefig(ofname)
        log.info("Saved to " + ofname)

  plt.show()


if __name__ == '__main__':
  main()
