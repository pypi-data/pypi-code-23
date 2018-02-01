# -*- coding: utf8 -*-

from .legit.scam.luqum.tree import SearchField, Word, AndOperation, OrOperation
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

    def visit_operation(self, klass, node, parents):
        def enum_children():
            for child in node.children:
                if isinstance(child, FunctionSplit):
                    continue

                yield child

        def has_split_function():
            for child in node.children:
                if isinstance(child, FunctionSplit):
                    return True

            return False

        has_split = has_split_function()

        if not has_split:
            return node

        children = list(enum_children())

        new_node = klass(*children)
        phase_search = SearchField('_phase', Word(self.__phase))

        return AndOperation(new_node, phase_search)

    def visit_and_operation(self, node, parents=None):
        return self.visit_operation(AndOperation, node, parents)

    def visit_or_operation(self, node, parents=None):
        return self.visit_operation(OrOperation, node, parents)

    def __call__(self, tree):
        return self.visit(tree)
