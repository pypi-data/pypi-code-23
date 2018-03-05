import abc


class Action(object):

    def __init__(self, name, signature, addlist, dellist, precondition):
        self.name = name
        self.signature = signature
        self.addlist = addlist
        self.dellist = dellist
        self.precondition = precondition

    def action_string(self, dictionary):
        params = " ".join([dictionary[var[0]] for var in self.signature])
        return "(" + self.name + " " + params + ")"

    @staticmethod
    def get_entry(param_mapping, predicate):
        names = [x for x in predicate]
        entry = tuple([param_mapping[name][0] for name in names])
        return entry

    def entries_from_list(self, preds, param_mapping):
        return [(pred[0], self.get_entry(param_mapping, pred[1])) for pred in preds]

    def to_delete(self, param_mapping):
        return self.entries_from_list(self.dellist, param_mapping)

    def to_add(self, param_mapping):
        return self.entries_from_list(self.addlist, param_mapping)

    def get_param_mapping(self, params):
        param_mapping = dict()
        for (name, param_type), obj in zip(self.signature, params):
            param_mapping[name] = obj
        return param_mapping


class Predicate(object):

    def __init__(self, name, signature):
        self.name = name
        self.signature = signature

    def ground(self, dictionary):
        return tuple([dictionary[x][0] for x in self.signature])

    def test(self, param_mapping, state):
        return self.ground(param_mapping) in state[self.name]


class ConditionVisitor():
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def visit_literal(self, literal):
        pass

    @abc.abstractmethod
    def visit_conjunction(self, conjunction):
        pass

    @abc.abstractmethod
    def visit_disjunction(self, conjunction):
        pass


class Condition():
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def accept(self, visitor):
        pass

    @abc.abstractmethod
    def test(self, mapping):
        pass


class Literal(Condition):

    def __init__(self, predicate, args):
        self.predicate = predicate
        self.args = tuple(args)

    def accept(self, visitor):
        return visitor.visit_literal(self)

    def test(self, mapping):
        return self.args in mapping[self.predicate]


class JunctorCondition(Condition):

    def __init__(self, parts):
        self.parts = parts


class Conjunction(JunctorCondition):

    def accept(self, visitor):
        return visitor.visit_conjunction(self)

    def test(self, mapping):
        return all([part.test(mapping) for part in self.parts])


class Disjunction(JunctorCondition):

    def accept(self, visitor):
        return visitor.visit_disjunction(self)

    def test(self, mapping):
        return all([part.test(mapping) for part in self.parts])


class StripsStringVisitor(ConditionVisitor):

    def visit_literal(self, condition):
        return "({} {})".format(condition.predicate, ' '.join(condition.args))

    def join_parts(self, condition):
        return ' '.join([part.accept(self) for part in condition.parts])

    def visit_conjunction(self, condition):
        return "(and {})".format(self.join_parts(condition))

    def visit_disjunction(self, condition):
        return "(or {})".format(self.join_parts(condition))


class PreconditionFalseError(Exception):
    pass
