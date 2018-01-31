# -*- coding: utf8 -*-

from .legit.scam.luqum.tree import SearchField, Word, AndOperation
from .legit.scam.luqum.utils import LuceneTreeTransformer
from .legit.scam import MLQueryVisitor, FunctionSplit


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

    def visit_operation(self, node, parents):
        def enum_children():
            for child in node.children:
                if isinstance(child, FunctionSplit):
                    yield SearchField('_phase', Word(self.__phase))

                yield child

        new_node = AndOperation(*list(enum_children()))

        return new_node

    def visit_and_operation(self, node, parents=None):
        return self.visit_operation(node, parents)

    def visit_or_operation(self, node, parents=None):
        return self.visit_operation(node, parents)

    def __call__(self, tree):
        return self.visit(tree)
