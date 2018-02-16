"""
Created on 16 mrt. 2017

@author: Matthijs Kruger
"""
from converter import excel_lib
from .excel_util import is_range, split_range, split_address, get_linest_degree

class ASTNode(object):
    """A generic node in the AST"""

    def __init__(self, token):
        super(ASTNode, self).__init__()
        self.token = token

    def __str__(self):
        return self.token.tvalue

    def __getattr__(self, name):
        return getattr(self.token, name)

    def children(self, ast):
        args = ast.predecessors(self)
        args = sorted(args, key=lambda x: ast.node[x]['pos'])
        # args.reverse()
        return args

    def parent(self, ast):
        args = ast.successors(self)
        return args if args else None

    def emit(self, ast, context=None):
        """Emit code"""
        # self.token.tvalue

class OperatorNode(ASTNode):
    def __init__(self, *args):
        super(OperatorNode, self).__init__(*args)

        # convert the operator to python equivalents
        self.opmap = {
            "^": "**",
            "=": "==",
            "&": "+",
            "": "+",  # union
            "<>": "!=",  # Added to support the <> (not equals), as <> doesn't seem to work and != does
        }

    def emit(self, ast, context=None):
        xop = self.tvalue
        args = self.children(ast)  # Get the arguments
        op = self.opmap.get(xop, xop)

        if self.ttype == "operator-prefix":
            return "-" + args[0].emit(ast, context=context)

        parent = self.parent(ast)
        # don't render the ^{1,2,..} part in a linest formula
        # TODO: bit of a hack
        ss = None
        if op == "**":
            if parent is not None and parent == "linest":
                return emit_arg(args, ast, context, 0)

        if op == "<" or op == "<=":
            # aa = emit_arg(args, ast, context, 0)
            # ss = "(" + aa + " if " + aa + " is not None else float('inf'))" + op + emit_arg(args, ast, context, 1)
            ss = surround('less_then', emit_arg(args, ast, context, 0), emit_arg(args, ast, context, 1),
                          str(op == '<='))
        elif op == ">" or op == ">=":
            # aa = emit_arg(args, ast, context, 1)
            # ss = emit_arg(args, ast, context, 0) + op + "(" + aa + " if " + aa + " is not None else float('inf'))"
            ss = surround('greater_then', emit_arg(args, ast, context, 0), emit_arg(args, ast, context, 1),
                          str(op == '>='))
        elif xop == '&' and op == '+':
            ss = to_safe_str(emit_arg(args, ast, context, 0)) + op + to_safe_str(emit_arg(args, ast, context, 1))
            # ss = 'safe_str(' + emit_arg(args, ast, context, 0) + ')' + op +
            # 'safe_str(' + emit_arg(args, ast, context, 1) + ')'
        elif op == '*':
            ss = surround('multiply', emit_arg(args, ast, context, 0), emit_arg(args, ast, context, 1))
        elif op == '/':
            ss = surround('divide', emit_arg(args, ast, context, 0), emit_arg(args, ast, context, 1))
        elif op == '+':
            ss = surround('plus', emit_arg(args, ast, context, 0), emit_arg(args, ast, context, 1))
        elif op == '-':
            ss = surround('minus', emit_arg(args, ast, context, 0), emit_arg(args, ast, context, 1))
        else:
            ss = emit_arg(args, ast, context, 0) + op + emit_arg(args, ast, context, 1)

        # avoid needless parentheses
        if ss and parent and not isinstance(parent, FunctionNode):
            ss = "(" + ss + ")"

        return ss

def emit_arg(args, ast, context, index):
    return args[index].emit(ast, context=context)

def surround(fn_name, *args):
    return fn_name + '(' + ",".join([n for n in args]) + ')'

def to_safe_str(value):
    return surround("safe_str", value)

class OperandNode(ASTNode):
    def __init__(self, *args):
        super(OperandNode, self).__init__(*args)

    def emit(self, ast, context=None):
        t = self.tsubtype

        if t == "logical":
            return str(self.tvalue.lower() == "true")
        elif t == "text" or t == "error":
            # if the string contains quotes, escape them
            val = self.tvalue.replace('"', '\\"')
            return '"' + val + '"'
        else:
            return str(self.tvalue)

class RangeNode(OperandNode):
    """Represents a spreadsheet cell or range, e.g., A5 or B3:C20"""
    def __init__(self, *args):
        super(RangeNode, self).__init__(*args)

    def emit(self, ast, context=None):
        # resolve the range into cells
        rng = self.tvalue.replace('$', '')
        sheet = context.curcell.sheet + "!" if context else ""
        if is_range(rng):
            sh, start, end = split_range(rng)
            if sh is not None:
                ss = 'eval_range("' + rng + '")'
            else:
                ss = 'eval_range("' + sheet + rng + '")'
        else:
            sh, col, row = split_address(rng)
            if sh is not None:
                ss = 'eval_cell("' + rng + '")'
            else:
                ss = 'eval_cell("' + sheet + rng + '")'
        return ss

class FunctionNode(ASTNode):
    """AST node representing a function call"""
    def __init__(self, *args):
        super(FunctionNode, self).__init__(*args)
        self.numargs = 0

        # map excel functions onto their python equivalents
        self.funmap = excel_lib.FUNCTION_MAP

    def emit(self, ast, context=None):
        fun = self.tvalue.lower()
        expr = ''

        # Get the arguments
        args = None
        if len(ast.pred) > 0:
            args = self.children(ast)

        if fun == "atan2":
            # swap arguments
            expr = "atan2(%s,%s)" % (emit_arg(args, ast, context, 1), emit_arg(args, ast, context, 0))
        elif fun == "pi":
            # constant, no parents
            expr = "pi"
        elif fun == "sin":
            expr = "sin(%s,%s)" % (emit_arg(args, ast, context, 0), emit_arg(args, ast, context, 0))
        elif fun == "if":
            # inline the if
            if len(args) == 2:
                expr = "%s if %s else 0" % (emit_arg(args, ast, context, 1), emit_arg(args, ast, context, 0))
            elif len(args) == 3:
                expr = "(%s if %s else %s)" % (emit_arg(args, ast, context, 1), emit_arg(args, ast, context, 0),
                                               emit_arg(args, ast, context, 2))
            else:
                raise Exception("if with %s arguments not supported" % len(args))

        elif fun == "array":
            expr += '['
            if len(args) == 1:
                # only one row
                expr += emit_arg(args, ast, context, 0)
            else:
                # multiple rows
                expr += ",".join(['[' + n.emit(ast, context=context) + ']' for n in args])

            expr += ']'
        elif fun == "arrayrow":
            # simply create a list
            expr += ",".join([n.emit(ast, context=context) for n in args])
        elif fun == "linest" or fun == "linestmario":

            expr = fun + "(" + ",".join([n.emit(ast, context=context) for n in args])

            if not context:
                degree, coef = -1, -1
            else:
                # linests are often used as part of an array formula spanning multiple cells,
                # one cell for each coefficient.  We have to figure out where we currently are
                # in that range
                degree, coef = get_linest_degree(context.excel, context.curcell)

            # if we are the only linest (degree is one) and linest is nested -> return vector
            # else return the coef.
            if degree == 1 and self.parent(ast):
                if fun == "linest":
                    expr += ",degree=%s)" % degree
                else:
                    expr += ")"
            else:
                if fun == "linest":
                    expr += ",degree=%s)[%s]" % (degree, coef - 1)
                else:
                    expr += ")[%s]" % (coef - 1)

        elif fun == "and":
            expr = "all([" + ",".join([n.emit(ast, context=context) for n in args]) + "])"
        elif fun == "or":
            expr = "any([" + ",".join([n.emit(ast, context=context) for n in args]) + "])"
        elif fun == "not":
            if len(args) > 1: raise Exception("Too many arguments for NOT function (1 expected): [%s], args: [%s]",
                                              len(args), args)
            expr = "not(" + ",".join([n.emit(ast, context=context) for n in args]) + ")"
        elif fun == "row":
            f = self.funmap.get(fun, fun)
            if args is None or len(args) == 0:
                sh, ad = context.curcell.address().split('!')
                args = [ad]
                expr = f + '("' + ",".join([n.replace('"', '\\"') for n in args]) + '")'
            else:
                expr = f + '("' + ",".join([n.tvalue.replace('"', '\\"') for n in args]) + '")'
        else:
            # map to the correct name
            f = self.funmap.get(fun, fun)
            expr = f + "(self, " + ",".join([n.emit(ast, context=context) for n in args]) + ")"
        return expr
