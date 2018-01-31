# dormouse: Parsing Python code into Boolean expressions
# Copyright (C) 2018  EPFL
#
# Permission is hereby granted, free of charge, to any person
# obtaining a copy of this software and associated documentation
# files (the "Software"), to deal in the Software without
# restriction, including without limitation the rights to use,
# copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the
# Software is furnished to do so, subject to the following
# conditions:
#
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES
# OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
# HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
# WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
# OTHER DEALINGS IN THE SOFTWARE.

import ast
import functools
import inspect
import itertools
import sympy

class NodeToExpression(ast.NodeVisitor):
    def __init__(self):
        self.args = []

    def visit_Module(self, node):
        if len(node.body) != 1:
            raise BaseException("Body has more than one element: {}", ast.dump(node.body))
        
        body = node.body[0]
        if isinstance(body, ast.FunctionDef) or isinstance(body, ast.Assign):
            return self.visit(body)

        raise BaseException("Unknown body type: {}", ast.dump(body))

    def visit_FunctionDef(self, node):
        args = [x.arg for x in node.args.args]
        self.symbols = dict(zip(args, sympy.symbols(args)))
        self.args = args

        for anode in node.body[:-1]:
            if not isinstance(anode, ast.Assign):
                raise BaseException("Body must contain of assigns followed by return statement: {}", ast.dump(anode))
            if len(anode.targets) != 1:
                raise BaseException("Assignment must have a single target: {}", ast.dump(anode))
            target = anode.targets[0]
            if not isinstance(target, ast.Name):
                raise BaseException("Assignment target must be a variable name: {}", ast.dump(target))
            name = target.id
            if name in self.symbols:
                raise BaseException("Variable name {} already assigned", name)
            self.symbols[name] = self.visit(anode.value)

        ret = node.body[-1]
        if not isinstance(ret, ast.Return):
                raise BaseException("Body must contain of assigns followed by return statement: {}", ast.dump(ret))
        return self.visit(ret)

    def visit_Lambda(self, node):
        args = [x.arg for x in node.args.args]
        self.symbols = dict(zip(args, sympy.symbols(args)))
        self.args = args
        
        return self.visit(node.body)

    def visit_Assign(self, node):
        return self.visit(node.value)

    def visit_Return(self, node):
        return self.visit(node.value)

    def visit_BoolOp(self, node):
        import _ast
        
        if len(node.values) < 2:
            raise BaseException("Too few values: {}", node.values)

        symbols = {_ast.Or: sympy.Or, _ast.And: sympy.And}
        exprs = [self.visit(v) for v in node.values]
        return symbols[type(node.op)]( *exprs ) 

    def visit_BinOp(self, node):
        import _ast

        symbols = {_ast.BitXor: sympy.Xor, _ast.BitOr: sympy.Or, _ast.BitAnd: sympy.And}
        return symbols[type(node.op)](self.visit(node.left), self.visit(node.right))

    def visit_Compare(self, node):
        import _ast

        if len(node.ops) != 1 or len(node.comparators) != 1:
            raise BaseException("Only single operator and single comparator comparison possible: {}", ast.dump(node))
    
        symbols = {_ast.NotEq: lambda a, b: a ^ b, _ast.Lt: lambda a, b: ~a & b, _ast.Gt: lambda a, b: a & ~b}

        return symbols[type(node.ops[0])](self.visit(node.left), self.visit(node.comparators[0]))

    def visit_IfExp(self, node):
        return sympy.ITE(self.visit(node.test), self.visit(node.body), self.visit(node.orelse))

    def visit_Call(self, node):
        source = inspect.getsource(eval(node.func.id)).strip()
        fnode = ast.parse(source)

        print(fnode)
        assert False

    def visit_Name(self, node):
        return self.symbols[node.id]

    def visit_NameConstant(self, node):
        if node.value == True:
            return sympy.true
        if node.value == False:
            return sympy.false
        raise BaseException("Unknown name constant: {}".format(ast.dump(node)))

    def generic_visit(self, node):
        raise BaseException("Unknown node: {}".format(ast.dump(node)))

def _parse(func):
    # Some corner cases
    if func == True: return sympy.true, []
    if func == False: return sympy.false, []

    source = inspect.getsource(func).strip()
    node = ast.parse(source)

    visitor = NodeToExpression()
    expr = visitor.visit(node)
    return expr, visitor.args

def to_truth_table(func):
    """
    Translates Python code into truth table (represented as integer)
    """
    sfunc, args = _parse(func)
    symbols = sympy.symbols(args)
    return sum((1 if sympy.simplify_logic(sfunc.subs(zip(symbols, reversed(bs)))) else 0) << i for i, bs in enumerate(itertools.product([False, True], repeat = len(symbols))))

def to_binary_truth_table(func):
    """
    Translates Python code into truth table (represented as binary string)
    """
    sfunc, args = _parse(func)
    symbols = sympy.symbols(args)
    return ''.join(reversed([('1' if sympy.simplify_logic(sfunc.subs(zip(symbols, reversed(bs)))) else '0') for bs in itertools.product([False, True], repeat = len(symbols))]))

def to_hex_truth_table(func):
    """
    Translates Python code into truth table (represented as hex string)
    """
    sfunc, args = _parse(func)
    symbols = sympy.symbols(args)
    nargs = len(symbols)
    v = sum((1 if sympy.simplify_logic(sfunc.subs(zip(symbols, reversed(bs)))) else 0) << i for i, bs in enumerate(itertools.product([False, True], repeat = nargs)))
    return "{:0{}x}".format(v, max(1, 2**(nargs - 2)))

def to_boolean_function(func):
    """
    Translates Python code into logic expression
    """

    expr, _ = _parse(func)
    return expr
