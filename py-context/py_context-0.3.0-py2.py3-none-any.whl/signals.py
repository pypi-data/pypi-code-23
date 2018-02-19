# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function, unicode_literals

from blinker import Namespace


signals = Namespace()

context_initialized = signals.signal('context_initialized')
pre_context_changed = signals.signal('pre_context_changed')
post_context_changed = signals.signal('post_context_changed')
context_key_changed = signals.signal('context_key_changed')
