# -*- coding: utf8 -*-

from .legit.scam.luqum.tree import SearchField, Word, AndOperation, OrOperation
from .legit.scam.luqum.utils import LuceneTreeTransformer
from .legit.scam import MLQueryVisitor, FunctionSplit


# noinspection PyClassicStyleClass
class SplitVisitor(MLQueryVisitor):
    def __init__(self):
        self.__split = {'train': 1.0}
        self.__split_field = None

    def has_phase(self, phase):
        return self.__split.get(phase) is not None

    def generic_visit(self, node, parents=None, context=None):
        pass

    def visit_function_split(self, node, parents, context):
        self.__split = node.split
        self.__split_field = node.split_field

    def get(self, phase):
        return self.__split.get(phase)


# noinspection PyClassicStyleClass
class GroupVisitor(MLQueryVisitor):
    def __init__(self):
        self.group = None

    def generic_visit(self, node, parents=None, context=None):
        pass

    def visit_function_group(self, node, parents, context):
        self.group = node.group


# noinspection PyClassicStyleClass
class RemoveSplitTransformer(LuceneTreeTransformer):
    def __init__(self, phase):
        self.__phase = phase

    def __create_phase_search(self):
        return SearchField('_phase', Word(self.__phase))

    def visit_function_split(self, node, parents):
        return self.__create_phase_search()

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
        phase_search = self.__create_phase_search()

        return AndOperation(new_node, phase_search)

    def visit_and_operation(self, node, parents=None):
        return self.visit_operation(AndOperation, node, parents)

    def visit_or_operation(self, node, parents=None):
        return self.visit_operation(OrOperation, node, parents)

    def __call__(self, tree):
        return self.visit(tree)
