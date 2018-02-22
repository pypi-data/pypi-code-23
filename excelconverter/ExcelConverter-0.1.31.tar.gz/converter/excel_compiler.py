# Excel compiler.
# creates nodes from cells puts them in a graph and then puts that graph in a cellmap.
# Has several functions to set and calculate the changed values

import networkx as nx
from networkx.classes.digraph import DiGraph
from .excel_node import *
from .excel_util import *
from .excel_lib import *
from .excel_wrapper import ExcelOpxWrapper as ExcelWrapperImpl
from .excel_wrapper import OpxRange
from .tokenizer import ExcelParser, f_token
logger = logging.getLogger(__name__)

# Set the sheet into a node
def add_node_to_graph(g, n):
    g.add_node(n)
    g.node[n]['sheet'] = n.sheet

    if isinstance(n, Cell):
        g.node[n]['label'] = n.col + str(n.row)
    else:
        # strip the sheet
        g.node[n]['label'] = n.address()[n.address().find('!') + 1:]

class ExcelCompiler(object):

    def __init__(self, filename=None, *args, **kwargs):
        # Load file
        super(ExcelCompiler, self).__init__()
        self.filename = filename
        # Set the filename
        self.excel = ExcelWrapperImpl(filename=filename)
        self.excel.connect()

        self.log = logging.getLogger("decode.{0}".format(self.__class__.__name__))

    def cell2code(self, cell):
        # Generate python code for the given cell
        if cell.formula is not None:
            exp = shunting_yard(cell.formula or str(cell.value))
            if exp is None or len(exp) == 0:
                raise Exception("Incorrect expression: [%s], cell: [%s], "
                                "cell.formula: [%s], cell.value: [%s]"
                                % (exp, cell, cell.formula, cell.value))

            # Correct the ranges found concerning the excel max col and row
            for e in exp:
                if isinstance(e, RangeNode):
                    e.token.tvalue = correct_range_single(self.excel, e.token.tvalue, cell.sheet)

            ast, root = build_ast(exp)
            code = root.emit(ast, context=Context(cell, self.excel))
        elif isinstance(cell.value, str) and re.match('[A-Za-z]+', cell.value):
            ast = None
            code = cell.value
        else:
            ast = None
            code = str('"' + cell.value + '"' if isinstance(cell.value, str) else cell.value)

        return code, ast

    def gen_graph(self, rng, sheet=None):
        return self.gen_graph_multi({sheet: rng})

    """
    Example usage:
        gen_graph({'Output1': 'A1:B5', 'Output2': 'A1:E8'})
        gen_graph({'Output1': '[A1:B5, AB4:FE85]', 'Output2': 'A1:E8'})
    """

    def gen_graph_multi(self, ranges):
        # When given a starting point (e.g., A6 or A3:B7) on a particular sheet,
        # generate a Spreadsheet instance that captures the logic and control flow of the equations

        # starting points
        # cursheet = sheet if sheet else self.excel.get_active_sheet()
        # self.excel.set_sheet(cursheet)

        # no need to output NumberRows and NumberColumns here,
        # since seed can be a list of unlinked cells
        seeds = None
        try:
            seeds = Cell.make_cells_multi(self.excel, ranges)
            if logger.isEnabledFor(logging.DEBUG):
                logger.info("Ranges [%s] expanded into [%s] cell_len", ranges, seeds)
            return self.gen_graph_intern(seeds)
        except Exception as ex:
            raise Exception("Error making cells, ranges: [%s], "
                            "excel: [%s]" % (ranges, self.excel)) from ex

    def gen_graph_intern(self, seeds):
        # only keep seeds with formulas or numbers
        # Scan seeds for data_types int, float or strings
        seeds = [s for s in seeds if s.formula or
                 isinstance(s.value, (int, float, str))]

        if logger.isEnabledFor(logging.DEBUG):
            logger.debug("Filtered seeds (keeping formulas, "
                         "strings, ints, floats): [%s] ", len(seeds))

        todo = [s for s in seeds if s.formula]

        if logger.isEnabledFor(logging.DEBUG):
            logger.info("Todo cells length: [%s]", len(todo))

        # map of all cells
        cellmap = dict([(x.address(), x) for x in seeds])

        # directed graph
        graph = nx.DiGraph()

        # match the info in cellmap
        for c in list(cellmap.values()):
            add_node_to_graph(graph, c)

        cursheet = self.excel.get_active_sheet()
        while todo:
            c1 = todo.pop()
            if logger.isEnabledFor(logging.DEBUG):
                logger.debug("Processing formula cell: [%s]", c1)

            # set the current sheet so relative addresses resolve properly
            if c1.sheet != cursheet:
                cursheet = c1.sheet
                self.excel.set_sheet(cursheet)

            try:
                pystr, ast = self.cell2code(c1)  # parse the formula into code
                c1.python_expression = pystr  # set the code & compile it (will flag problems sooner rather than later)
                c1.compile()
            except Exception as ex:
                raise Exception(
                    "Error compiling/cell2code cell: [%s], todo length: [%s]" % (c1, len(todo))) from ex

            if ast is not None:
                # get all the cells/ranges this formula refers to
                # No need to correct for '$' as it has been moved to the cell2node() function
                deps = [x.tvalue for x in ast.nodes() if isinstance(x, RangeNode)]
                deps = uniqueify(deps)  # remove dupes
                # deps = [x.tvalue.replace('$', '') for x in ast.nodes() if isinstance(x, RangeNode)]
                # deps = uniqueify(deps)  # remove dupes

                for dep in deps:
                    # Ensure to always set the active sheet, especially in case no dependency sheet is found,
                    # that means the dependency occurs on the same sheet as cursheet,
                    # but in case we just had a dependency to another
                    # sheet that can result in using the wrong sheet if not set.
                    dep_sheet = create_sheet(dep)
                    dep_sheet = dep_sheet if dep_sheet else cursheet
                    self.excel.set_sheet(dep_sheet if dep_sheet else cursheet)

                    if logger.isEnabledFor(logging.DEBUG):
                        logger.debug("Processing dependency [%s!%s] of formula cell: [%s]", dep_sheet, dep, c1)

                    # if the dependency is a multi-cell range, create a range object
                    rng_address, rng = None, None
                    if is_range(dep):
                        try:
                            cells, nrows, ncols, rng_details = Cell.make_cells(self.excel, dep, sheet=dep_sheet,
                                                                               parent_ast=ast, cellmap=cellmap)

                            # this will make sure we always have an absolute address
                            rng_address = create_address(rng_details, sheet=dep_sheet)

                            # No cells created if not needed (already exists in cell map)
                            if cells is None or rng_address in cellmap:
                                # already dealt with this range
                                # add an edge from the range to the parent
                                graph.add_edge(cellmap[rng_address], cellmap[c1.address()])

                                if logger.isEnabledFor(logging.DEBUG):
                                    logger.debug(
                                        "Skipping range dependency [%s] of dependency: [%s], "
                                        "of formula cell: [%s], already present",
                                        rng_address, dep, c1)
                                continue

                            # update the original range as the returned one is probably more specific if it wasn't a list
                            rng = CellRange(rng_details, dep, None, sheet=dep_sheet)
                            # cells, nrows, ncols = Cell.make_cells(self.excel, {cursheet: dep})

                            # save the range
                            # Ensure to use the original address to store it as other need it to find it.
                            cellmap[rng_address] = rng
                            # cellmap[rng.address()] = rng
                            # add an edge from the range to the parent
                            add_node_to_graph(graph, rng)
                            graph.add_edge(rng, cellmap[c1.address()])
                            # cells in the range should point to the range as their parent
                            target = rng
                        except Exception as ex:
                            raise Exception(
                                "Error making cells, cell: [%s], ast: [%s], dep: [%s], "
                                "rng address: [%s], rng: [%s], todo_len: [%s], seeds_len: [%s]" %
                                (c1, ast, dep, rng_address, rng, len(todo), len(seeds))) from ex
                    else:
                        # not a range, create the cell object
                        cells = (Cell.resolve_cell(self.excel, dep, sheet=dep_sheet),)
                        target = cellmap[c1.address()]

                    # process each cell
                    if logger.isEnabledFor(logging.DEBUG):
                        logger.debug("Adding [%s] row-cells for dependency [%s!%s]", len(cells), dep_sheet, dep)

                    for c2 in flatten(cells):
                        # Check that cells are None
                        if c2 is not None:
                            # if we haven't treated this cell already
                            if c2.address() in cellmap:
                                if logger.isEnabledFor(LOG_FINE):
                                    logger.log(LOG_FINE, "Skipping [%s] cell for dependency [%s!%s], "
                                                         "already present", c2,
                                               dep_sheet, dep)
                            else:
                                if c2.formula:
                                    # cell with a formula, needs to be added to the todo list
                                    todo.append(c2)
                                else:
                                    try:
                                        # constant cell, no need for further processing, just remember to set the code
                                        pystr, ast = self.cell2code(c2)
                                        c2.python_expression = pystr
                                        c2.compile()
                                    except Exception as ex:
                                        raise Exception(
                                            "Error compiling/cell2code dependency cell, cell dep: [%s] cell: [%s], "
                                            "ast: [%s], dep: [%s], "
                                            "todo: [%s], seeds: [%s]" % (c2, c1, ast, dep, todo, seeds)) from ex

                                # save in the cellmap
                                if logger.isEnabledFor(LOG_FINE):
                                    logger.log(LOG_FINE, "Adding cell [%s] to cellmap for dependency [%s!%s]", c2,
                                               dep_sheet, dep)
                                cellmap[c2.address()] = c2
                                # add to the graph
                                add_node_to_graph(graph, c2)

                            # add an edge from the cell to the parent (range or cell)
                            graph.add_edge(cellmap[c2.address()], target)

        if logger.isEnabledFor(logging.INFO):
            logger.info("Graph construction done, %s nodes, %s edges, %s cellmap entries",
                        len(graph.nodes()), len(graph.edges()), len(cellmap))
        sp = Spreadsheet(graph, cellmap)
        return sp

def shunting_yard(expression):
    """
    Tokenize an excel formula expression into reverse polish notation

    Core algorithm taken from wikipedia with varargs extensions from
    http://www.kallisti.net.nz/blog/2008/02/extension-to-the-shunting-yard-algorithm-to-allow-variable-numbers-of-arguments-to-functions/
    """
    # remove leading =

    if expression.startswith('='):
        expression = expression[1:]

    p = ExcelParser()
    p.parse(expression)

    # insert tokens for '(' and ')', to make things clearer below
    tokens = []
    for t in p.tokens.items:
        if t.ttype == "function" and t.tsubtype == "start":
            t.tsubtype = ""
            tokens.append(t)
            tokens.append(f_token('(', 'arglist', 'start'))
        elif t.ttype == "function" and t.tsubtype == "stop":
            tokens.append(f_token(')', 'arglist', 'stop'))
        elif t.ttype == "subexpression" and t.tsubtype == "start":
            t.tvalue = '('
            tokens.append(t)
        elif t.ttype == "subexpression" and t.tsubtype == "stop":
            t.tvalue = ')'
            tokens.append(t)
        else:
            tokens.append(t)

    # http://office.microsoft.com/en-us/excel-help/calculation-operators-and-precedence-HP010078886.aspx
    operators = {':': Operator(':', 8, 'left'), '': Operator(' ', 8, 'left'), ',': Operator(',', 8, 'left'),
                 'u-': Operator('u-', 7, 'left'), '%': Operator('%', 6, 'left'), '^': Operator('^', 5, 'left'),
                 '*': Operator('*', 4, 'left'), '/': Operator('/', 4, 'left'), '+': Operator('+', 3, 'left'),
                 '-': Operator('-', 3, 'left'), '&': Operator('&', 2, 'left'), '=': Operator('=', 1, 'left'),
                 '<': Operator('<', 1, 'left'), '>': Operator('>', 1, 'left'), '<=': Operator('<=', 1, 'left'),
                 '>=': Operator('>=', 1, 'left'), '<>': Operator('<>', 1, 'left')}

    output = collections.deque()
    stack = []
    were_values = []
    arg_count = []

    for t in tokens:
        if t.ttype == "operand":

            output.append(create_node(t))
            if were_values:
                were_values.pop()
                were_values.append(True)

        elif t.ttype == "function":

            stack.append(t)
            arg_count.append(0)
            if were_values:
                were_values.pop()
                were_values.append(True)
            were_values.append(False)

        elif t.ttype == "argument":

            while stack and (stack[-1].tsubtype != "start"):
                output.append(create_node(stack.pop()))

            if were_values.pop():
                arg_count[-1] += 1
            were_values.append(False)

            if not len(stack):
                raise Exception("Mismatched or misplaced parentheses")

        elif t.ttype.startswith('operator'):

            if len(stack) > 0 and t.ttype.endswith('-prefix') and t.tvalue == "-":
                o1 = operators['u-']
            else:
                o1 = operators[t.tvalue]

            while stack and stack[-1].ttype.startswith('operator'):
                if stack[-1].ttype.endswith('-prefix') and stack[-1].tvalue == "-":
                    o2 = operators['u-']
                else:
                    o2 = operators[stack[-1].tvalue]

                if ((o1.associativity == "left" and o1.precedence <= o2.precedence)
                        or
                        (o1.associativity == "right" and o1.precedence < o2.precedence)):

                    output.append(create_node(stack.pop()))
                else:
                    break

            stack.append(t)

        elif t.tsubtype == "start":
            stack.append(t)

        elif t.tsubtype == "stop":

            while stack and stack[-1].tsubtype != "start":
                output.append(create_node(stack.pop()))

            if not stack:
                raise Exception("Mismatched or misplaced parentheses")

            stack.pop()

            if stack and stack[-1].ttype == "function":
                f = create_node(stack.pop())
                a = arg_count.pop()
                w = were_values.pop()
                if w:
                    a += 1
                f.num_args = a
                output.append(f)

    while stack:
        if stack[-1].tsubtype == "start" or stack[-1].tsubtype == "stop":
            raise Exception("Mismatched or misplaced parentheses")

        output.append(create_node(stack.pop()))

    # convert to list
    result = [x for x in output]
    return result

def build_ast(expression):
    """build an AST from an Excel formula expression in reverse polish notation"""

    # use a directed graph to store the tree
    graph = DiGraph()

    stack = []

    for n in expression:
        # Since the graph does not maintain the order of adding nodes/edges
        # add an extra attribute 'pos' so we can always sort to the correct order
        if isinstance(n, OperatorNode):
            if n.ttype == "operator-infix":
                arg2 = stack.pop()
                arg1 = stack.pop()
                graph.add_node(arg1, pos=1)
                graph.add_node(arg2, pos=2)
                graph.add_edge(arg1, n)
                graph.add_edge(arg2, n)
            else:
                arg1 = stack.pop()
                graph.add_node(arg1, pos=1)
                graph.add_edge(arg1, n)
        elif isinstance(n, FunctionNode):
            args = [stack.pop() for _ in range(n.num_args)]
            args.reverse()
            for i, a in enumerate(args):
                graph.add_node(a, pos=i)
                graph.add_edge(a, n)
                # for i in range(n.num_args):
                #    G.add_edge(stack.pop(),n)
        else:
            graph.add_node(n, pos=0)

        stack.append(n)

    if len(stack) < 1:
        raise Exception("Error building ast, expression: [%s], graph: [%s]" % (expression, graph))
    return graph, stack.pop()

class Context(object):
    """A small context object that nodes in the AST can use to emit code"""

    def __init__(self, curcell, excel):
        # the current cell for which we are generating code
        self.curcell = curcell
        # a handle to an excel instance
        self.excel = excel

def create_node(t):
    """Simple factory function"""
    if t.ttype == "operand":
        if t.tsubtype == "range":
            return RangeNode(t)
        else:
            return OperandNode(t)
    elif t.ttype == "function":
        return FunctionNode(t)
    elif t.ttype.startswith("operator"):
        return OperatorNode(t)
    else:
        return ASTNode(t)

class Operator:
    """Small wrapper class to manage operators during shunting yard"""

    def __init__(self, value, precedence, associativity):
        self.value = value
        self.precedence = precedence
        self.associativity = associativity

class Spreadsheet(object):

    def __init__(self, g, cellmap):
        super(Spreadsheet, self).__init__()
        self.graph = g
        self.cellmap = cellmap
        self.__call_stack = []
        self.params = None

    def contains(self, cell):
        return cell in self.cellmap

    def plot_graph(self):
        import matplotlib.pyplot as plt

        pos = nx.spring_layout(self.graph, iterations=2000)
        nx.draw_networkx_nodes(self.graph, pos)
        nx.draw_networkx_edges(self.graph, pos, arrows=True)
        nx.draw_networkx_labels(self.graph, pos)
        plt.show()

    def set_value(self, cell, val, is_addr=True):
        if is_addr is not None:
            cell = self.cellmap[cell]
            if cell.value != val:
                # We should always reset the successors when the value is changes,
                # also when it's changed from a None value
                # to a not-None value, else the others aren't informed, and will not reset it's value such that the old
                # value will be used when evaluated.

                self.reset_all(cell, True)
                cell.value = val
                # Because we set a value we indicate it as not-dirty. Suppose the cell contains a formula, like a
                # reference to another cell, setting the value will overwritte the behavior at that moment.
                # When we "read"
                # the value through evaluation, it would (if not indicating it as not-dirty) evaluate the formula as
                # it's dirty through the reset call in  this method, such that it will set/store the value of the
                # reference and overwrite the set value "manually" by calling this method (as if it wasn't set)
                # Note: till it will be reset, such that it becomes dirty,
                # the set value will be returned. When it's dirty
                # will be be evaluated that will result in using the referenced value (again)
                cell.dirty = False

    def reset(self, cell):
        self.reset_all(cell, not cell.dirty or isinstance(cell, CellRange))
        # self.reset_all(cell, cell.value is not None or isinstance(cell, CellRange))

    def reset_all(self, cell, reset_successors):
        if logger.isEnabledFor(LOG_FINE):
            logger.log(LOG_FINE, "Resetting cell, dirty: [%s], cell: [%s]", cell.dirty, cell)
        if cell.reset_inprogress:
            return  # Already been reset, let's skip it.
            # raise Exception("Cell reset in progress: [%s]" % (cell))
        try:
            cell.reset_inprogress = True
            # Note: we split the reset method,
            # as before it would only perform the reset in case the cell value isn't None
            # already. However, that was restricted
            # in case it was already None, such that a change in value would not reset
            # the successors such that the successors would use the old value.
            # CellRange instances are skipped as their value isn't used
            if isinstance(cell, Cell):
                cell.value = None

            # If already dirty, no need to continue, we assume that it's successors been made dirty as well.
            # The value of CellRange isn't used so we have to skip it
            if not cell.dirty or isinstance(cell, CellRange):
                if isinstance(cell, Cell):
                    cell.dirty = True
                if reset_successors:
                    if logger.isEnabledFor(LOG_FINE):
                        childs = '\n'.join(str(p) for p in self.graph.succ[cell].keys())
                        logger.log(LOG_FINE, "Resetting children of: [%s]:\n[%s]", cell.address(), childs)
                    list(map(self.reset, self.graph.successors(cell)))
        finally:
            cell.reset_inprogress = False

    def print_value_tree(self, addr, indent):
        cell = self.cellmap[addr]
        print(("%s %s = %s" % (" " * indent, addr, cell.value)))
        for c in self.graph.predecessors_iter(cell):
            self.print_value_tree(c.address(), indent + 1)

    # def recalculate(self, addr):
    #     for c in list(self.cellmap.values()):
    #         if isinstance(c, CellRange):
    #             self.evaluate_range(c, is_addr=False)
    #         else:
    #             self.evaluate(c, is_addr=False)
    #         return self.evaluate(c)

    # def evaluate_range(self, rng, is_addr=True):
    #     if is_addr:
    #         rng = self.cellmap[rng]
    #
    #     # its important that [] gets treated as false here
    #     if rng.value:
    #         return rng.value
    #     elif isinstance(rng.value, str):
    #         return rng.value
    #
    #     cells, nrows, ncols = rng.celladdress, rng.nrows, rng.ncols
    #     if 1 == nrows or 1 == ncols:
    #         data = [self.evaluate(c) for c in cells]
    #     else:
    #         data = [[self.evaluate(c) for c in cells[i]] for i in range(len(cells))]
    #
    #     # Ensure to indicate the CellRange instance isn't dirty anymore, else it will get ignored next time such that
    #     # it's successors aren't reset and return the wrong value (example: B1(Cell)->
    #     B1:B2(CellRange)-> Vlookup(Cell)
    #     rng.value = data
    #     rng.dirty = False
    #     return data

    def evaluate(self, cell, is_addr=True):
        if is_addr is not None:
            cell = self.cellmap[cell]
            if cell.eval_inprogress:
                raise Exception("Evaluation of cell already in progress, cell: [%s], call stack:\n%s"
                                % (cell, self.call_stack_string(self.__call_stack)))

            # We only evaluate cells that have a formula and are dirty. In case they aren't dirty we return their
            # current value. We don't check if the value isn't None, as None might be a valid result of a formula
            # which can cause infinite, or unnecessary loops

            if not cell.formula or not cell.dirty:
                return cell.value
                # if not cell.formula:
                #     return cell.value

        def eval_cell(address):
            # return address
            try:
                # Note: we have to evaluate the cell and return the value, else an expression like "A3+A4" will fail
                # as python will try to "add" strings. This expression is processed by python directly and not through
                # a function in the excel_lib
                value = self.evaluate(address)
                if not value:
                    try:
                        if value is None or len(value) == 0 and cell.formula:
                            # The split will fail in case it's not a valid cell address
                            split_address(cell.formula[1:])
                            # In case it concerns a cell reference,
                            # it should return 0 in case the references cell is None
                            value = 0
                    except Exception:
                        pass
                return value
            # return self.evaluate(address)
            except:
                raise self.create_exception("Problem evaluating cell [%s]", address)

        def eval_range(rng):
            try:
                # We return the range and let the "user" (function) decide when to evaluate.
                # Example: in case of a (v/h)lookup function we don't want to evaluate the complete search
                # range before feeding it to the lookup function, as the lookup function only use small parts
                # of the search rang. And evaluating a huge range can easily lead to circular references.
                return rng
                # return self.evaluate_range(rng)
            except:
                raise self.create_exception("Problem evaluating cell [%s]", rng)

        try:
            cell.eval_inprogress = True
            if logger.isEnabledFor(LOG_FINE):
                logger.log(LOG_FINE, "Evaluating: %s, %s", cell.address(), cell.python_expression)

            if is_eval_allowed(self, cell):
                # indicate it's not dirty anymore before evaluation occurs to overcome infinite recursive loops.
                cell.dirty = False

                self.__call_stack.append(str(cell))
                vv = eval(cell.compiled_expression)
            else:
                vv = cell.compiled_expression

            cell.dirty = False
            cell.value = vv
            digits = get_zeros(cell)

            if digits is not None:
                cell.value = round(cell.value, digits)


        except Exception as ex:
            if str(ex).startswith("Problem evaluating"):
                raise ex
            else:
                raise Exception(
                    "Problem evaluating: [%s], call stack: \n%s" % (
                        cell, self.call_stack_string(self.__call_stack))) from ex
        finally:
            cell.eval_inprogress = False
            self.__call_stack.pop()
            if len(self.__call_stack) > 10000:
                self.__call_stack = []
                logger.error("Call stack has reached maximum. Cell: [%s]", cell)

        # if isinstance(cell.value, (float, int)):
        #     round(cell.value, 2)
        return cell.value

    def create_exception(self, msg, rng):
        if rng in self.cellmap:
            rng = self.cellmap[rng]
        return Exception(msg % rng)

    def call_stack_string(self, call_stack):
        if len(call_stack) > 0:
            result = ''
            for x in call_stack:
                result += x + '\n'
            return result
        return ''
