# -*- coding: utf-8 -*-
#
# Copyright (c) 2017 -- Lars Heuer - Semagia <http://www.semagia.com/>.
# All rights reserved.
#
# License: BSD License
#
"""\
Integration into Jinja.
"""
from __future__ import absolute_import, unicode_literals
import segno


def register(env, qr='qr', mqr= 'mqr'):
    """\

    :param env: The Jinja environment.
    """
    register_qr(env, qr)
    register_mqr(env, mqr)


def register_qr(env, qr='qr'):
    """\

    """
    env.filters[qr] = make_qr


def register_mqr(env, mqr='mqr'):
    """\

    """
    env.filters[mqr] = make_mqr


def make_qr():
    """\

    """


def make_mqr():
    """\

    """
    