# -*- coding: utf-8

from IPython.display import display, FileLink

import sys
import re

from .utils import *

modes = [
    "sync",
    "async",
    "general"
]


def bn2smv(bnfile, mode, init=None, name=None):
    assert mode in modes, "Le dernier argument doit être parmis %s" % " ".join(modes)

    hide = False
    if isinstance(bnfile, dict):
        defs = bnfile
        if not name:
            name = "tmpbn"
            hide = True
    else:
        name = name or bnfile.replace(".bn", "")
        defs = read_bn(bnfile)

    smvfile = "%s-%s.smv" % (name, mode)

    dom = list(sorted(defs.keys()))
    udom = ["u%s" % n for n in dom]

    def var(n):
        if isinstance(n, int):
            return "x%d" % n
        return n

    lines = ["MODULE main"]
    lines.append("VAR")
    for i in dom:
        lines.append("%s: boolean;" % var(i))
    lines.append("ASSIGN")
    for i in dom:
        if mode == "sync":
            lines.append("next(%s) := f%s;" % (var(i),i))
        else:
            lines.append("next(%s) := {%s, f%s};" % (var(i),var(i),i))
    lines.append("DEFINE")
    for d in sorted(defs.items()):
        lines.append("f%s := %s;" % d)
    if mode != "sync":
        lines.append("FIXEDPOINTS := %s;" \
            % (" & ".join(["%s = f%s" % (var(i),i) for i in dom])))
        lines.append("TRANS")
        lines.append("  FIXEDPOINTS")
        if mode == "general":
            for i in dom:
                lines.append("| next(%s) != %s" % (var(i),var(i)))
        elif mode == "async":
            for i in dom:
                freeze = " & ".join(["next({0})={0}".format(var(j)) for j in dom if i != j])
                freeze = " & %s" % freeze if freeze else ""
                lines.append("| next({0})!={0}{1}".format(var(i),freeze))
        lines.append(";")
    lines.append("")
    lines.append("-- INIT XXXX;")
    lines.append("-- CTLSPEC XXXX;")
    lines.append("-- LTLSPEC XXXX;")
    lines.append("")

    open(smvfile, "w").write("\n".join(lines))
    if not hide:
        display(FileLink(smvfile, url_prefix="../edit/"))

    if init is not None:
        for n in init:
            assert n in defs, "Nœud %s inconnu" % repr(n)
        smv_init = []
        for n in sorted(defs):
            smv_init.append("%s%s" % ("!" if n not in init else "" ,var(n)))
        append_line(smvfile, "INIT %s;" % (" & ".join(smv_init)))

    return smvfile


