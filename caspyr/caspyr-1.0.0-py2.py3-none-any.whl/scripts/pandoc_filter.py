#!/usr/bin/env python
r"""Replaces:
  `figure`   : `figure*` if width=\textwidth
  `\[ ... \] : equation

Usage:
  pandoc_filter [--help|options] <type> [<file>]

Options:
  -h, --help     : Print this help and exit
  -v, --version  : Print module version number and exit
  --no-deqn      : bool, don't subsitiute \[\] -> \begin{equation}\end{equation}
  --MMD=<fmt>    : Output Makefile include information for DEPENDANT to FILE,
                   where `<fmt>` is `FILE:DEPENDANT`
  -p=<P>, --image-prefix=<P>  : for `--MMD`, e.g. "images/" [default: "":str]
  --log=<lvl>    : CRITICAL|WARN(ING)|[default: INFO]|DEBUG|NOTSET

Arguments:
  <type>  : inplace|fromfile|(default: stdin|-)
      default (if unknown) is `stdin`. `fromfile` writes to `stdout`
  <file>  : *|(default: -).md|html|(default: latex)
"""
import sys
import re
from argopt import argopt
import logging
__author__ = "Casper da Costa-Luis <casper.dcl@physics.org>"
__all__ = ["main"]
__version__ = "0.3.1"


RE_TEX_WFIG = re.compile(
    r"(\\begin\{figure)(\})(\s*\\centering\s*" +
    r"\\includegraphics\[width=1\.?[0]*\\textwidth\].*?\\end\{figure)(\})",
    flags=re.M | re.S)
RE_TEX_DEQN = re.compile(r"\\\[([\s\S]*?)\\\]", flags=re.M)
RE_MD_NOTES = re.compile(r"^[Nn]otes?:\s*(\S.*?)\n\n", flags=re.M | re.S)
RE_LONGTAB_COL = re.compile(
    r"(\\begin\{minipage\}\[)t(\]\{[0-9.]+\\columnwidth\})", flags=re.M)
# sed -rn 's/.*!\[.*\]\(([^):]+)\).*/\1/p' "$<" | xargs echo "$@": > "$(<:%.md=$(DOUT)/%.d)"
RE_MD_IMG = re.compile(r"\!\[.*?\]\(\s*([^):]+?)\)", flags=re.M | re.S)
# sed -rn 's/.*\\includegraphics[^{]*\{([^}]+)\}.*/images\/\1/p' "$<" | xargs echo "$@": > "$(<:%.latex=%.d)"
RE_TEX_IMG = re.compile(
    r"\\includegraphics(\[[^]]*\])?\{([^}]+)\}", flags=re.M | re.S)
RE_MD_REFS = re.compile(r" +(\[@.*?\])", flags=re.M)


def run(args):
  log = logging.getLogger(__name__)

  if not args.file:
    args.file = '-.latex'
  basename, ext = [s.lower() for s in args.file.rsplit('.', 1)]
  if not ext:
    ext = "latex"
  log.info("ext:" + ext)

  # READ
  fp = open(args.file) if args.type in ["inplace", "fromfile"] \
      else sys.stdin
  raw = fp.read().replace("\r\n", "\n")
  fp.close()

  # FILTER
  if ext == "md":
    log.info("slide notes")
    raw = RE_MD_NOTES.sub(r'<div class="notes">\n\n\1\n\n</div>\n\n', raw)
    log.info("nbsp refs")
    raw = RE_MD_REFS.sub(r"&nbsp;\1", raw)
    if args.MMD:
      log.info("MMD:" + args.MMD)
      fn, dependant = args.MMD.split(':')
      with open(fn, "w") as fd:
        images = RE_MD_IMG.findall(raw)
        log.debug(images)
        if args.image_prefix:
          images = [args.image_prefix + i for i in images]
        fd.write(dependant + ": " + ' '.join(images))
  elif ext == "html":
    log.info("TeX-AMS_~~C~~HTML")
    raw = raw.replace("TeX-AMS_CHTML", "TeX-AMS_HTML")
  elif ext == "latex":
    log.info("wide figures")
    log.debug('\n---\n'.join(''.join(fig) for fig in RE_TEX_WFIG.findall(raw)))
    raw = RE_TEX_WFIG.sub(r"\1*\2\3*\4", raw)
    if not args.no_deqn:
      log.info("disp eqn's")
      raw = RE_TEX_DEQN.sub(r"\\begin{equation}\1\\end{equation}", raw)
    log.info("longtab")
    raw = RE_LONGTAB_COL.sub(r"\1\2", raw)
    # raw = RE_TEX_WFIG.sub(r"\\begin{strip}\1*\2[htbp]\3*\4\\end{strip}", raw)
    if args.MMD:
      log.info("MMD:" + args.MMD)
      fn, dependant = args.MMD.split(':')
      with open(fn, "w") as fd:
        images = [im for (_, im) in RE_TEX_IMG.findall(raw)]
        log.debug(images)
        if args.image_prefix:
          images = [args.image_prefix + i for i in images]
        fd.write(dependant + ": " + ' '.join(images))
  else:
    log.warn("ext not recogmised")

  # WRITE
  if args.type == "fromfile" or basename == '-':
    fp = sys.stdout
  else:
    fp = open(args.file, mode='w')
  fp.write(raw)
  fp.close()


def main(argv=None):
  """argv  : list, optional (default: sys.argv[1:])"""
  args = argopt(__doc__, version=__version__).parse_args(args=argv)
  logging.basicConfig(level=getattr(logging, args.log, logging.INFO))
  log = logging.getLogger(__name__)
  log.debug(args)
  return run(args) or 0


if __name__ == "__main__":
  main()
