from pythogic.misc.Formula import Formula
from pythogic.misc.Symbol import Symbol


class REfFormula(Formula):

    pass

class REfPropositionalFormula(REfFormula):
    def __init__(self, symbols:Set[Symbol]):
        self.symbols = symbols

    def _members(self):
        return (sorted(self.symbols))

    def __str__(self):
        return str(self.symbols)

    def __lt__(self, other):
        return "".join([s.name for s in self.symbols]).__lt__("".join([s.name for s in other.symbols]))


class REfUnion(REfFormula):
    operator_symbol = "+"
    def __init__(self, f1:REfFormula, f2:REfFormula):
        self.f1 = f1
        self.f2 = f2

    def __str__(self):
        return str(self.f1) + " " + self.operator_symbol + " " + str(self.f2)

    def _members(self):
        return (self.f1, self.operator_symbol, self.f2)


class REfSequence(REfFormula):
    operator_symbol = ";"

    def __init__(self, f1:REfFormula, f2:REfFormula):
        self.f1 = f1
        self.f2 = f2

    def __str__(self):
        return str(self.f1) + " " + self.operator_symbol + " " + str(self.f2)

    def _members(self):
        return (self.f1, self.operator_symbol, self.f2)

class REfStar(REfFormula):
    operator_symbol = "*"

    def __init__(self, f: REfFormula):
        self.f = f

    def __str__(self):
        return str(self.f) + " " + self.operator_symbol

    def _members(self):
        return (self.f, self.operator_symbol)



