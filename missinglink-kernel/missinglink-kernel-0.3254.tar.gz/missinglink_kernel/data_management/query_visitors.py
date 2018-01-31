# -*- coding: utf8 -*-

from .legit.scam.luqum.tree import SearchField, Word
from .legit.scam.luqum.utils import LuceneTreeTransformer
from .legit.scam import MLQueryVisitor


# noinspection PyClassicStyleClass
class SplitVisitor(MLQueryVisitor):
    def __init__(self):
        self.split = {'train': 1.0}
        self.split_field = None

    def generic_visit(self, node, parents=None, context=None):
        pass

    def visit_function_split(self, node, parents, context):
        self.split = node.split
        self.split_field = node.split_field


# noinspection PyClassicStyleClass
class RemoveSplitTransformer(LuceneTreeTransformer):
    def __init__(self, phase):
        self.__phase = phase

    def visit_function_split(self, node, parents):
        return SearchField('_phase', Word(self.__phase))

    def __call__(self, tree):
        return self.visit(tree)
