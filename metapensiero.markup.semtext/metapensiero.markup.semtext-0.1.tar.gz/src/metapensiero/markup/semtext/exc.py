# -*- coding: utf-8 -*-
# :Project:   metapensiero.markup.semtext -- Exceptions
# :Created:   sab 01 apr 2017 13:22:47 CEST
# :Author:    Lele Gaifax <lele@metapensiero.it>
# :License:   GNU General Public License version 3 or later
# :Copyright: © 2017 Arstecnica s.r.l.
# :Copyright: © 2018 Lele Gaifax
#

from .ast import Paragraph, Span, Text


class UnparsableError(ValueError):
    "Error raised when something goes wrong within the SEM parser"

    @property
    def message(self):
        "The error message"
        return self.args[0]

    @property
    def text(self):
        "The whole raw text wrapped inside a single paragraph"
        return Text([Paragraph([Span(self.args[1])])])
