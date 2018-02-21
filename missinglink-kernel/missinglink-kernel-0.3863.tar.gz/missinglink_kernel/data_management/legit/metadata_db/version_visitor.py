# -*- coding: utf8 -*-
from ..scam import MLQueryVisitor


# noinspection PyClassicStyleClass
class VersionVisitor(MLQueryVisitor):
    def __init__(self):
        self.version = None

    def generic_visit(self, node, parents=None, context=None):
        pass

    def visit_function_version(self, node, parents=None, context=None):
        self.version = node.version
