#!/usr/bin/env python
# -*- coding: utf-8 -*-


def exception_generator(name, parent = Exception, message=''):
    def __init__(self, **debugvars):
        lines = [message]
        if len(debugvars) > 0:
            lines.append('Printing debug variables:')
        for n, v in debugvars.items():
            lines.append(f'{n}: {v}')
        Exception.__init__(self, '\n'.join(lines))
    return type(name, (parent,), {'__init__': __init__})
