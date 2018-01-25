#!/usr/bin/env python
import os, sys 
from docutils import utils
from docutils.core import publish_parts
from public import public


@public
def rstvalidator(path):
    if not path:
        raise ValueError("path '' EMPTY")
    if not os.path.exists(path):
        raise OSError("%s NOT EXISTS" % path)

    reports = []

    def system_message(self, level, message, *children, **kwargs):
        args = [self, level, message] + list(children)
        result = orignal_system_message(*args, **kwargs)
        if level >= self.WARNING_LEVEL:
            # All reST failures preventing doc publishing go to reports
            # and thus will result to failed checkdocs run
            reports.append(message)
        return result

    def rst2html(value):
        """ Run rst2html translation """
        parts = publish_parts(source=value, writer_name="html4css1")
        return parts['whole']

    text = open(path).read()
    # Monkeypatch docutils for simple error/warning output support
    orignal_system_message = utils.Reporter.system_message
    utils.Reporter.system_message = system_message
    old_stderr = sys.stderr
    sys.stderr = open(os.devnull, "w")
    try:
        rst2html(text)
        utils.Reporter.system_message = orignal_system_message
        return reports
    finally:
        sys.stderr.close()
        sys.stderr = old_stderr
