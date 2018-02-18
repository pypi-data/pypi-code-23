import ast


_OPS = {
    ast.Eq: '=',
    ast.NotEq: '!=',
    ast.Gt: '>',
    ast.GtE: '>=',
    ast.Lt: '<',
    ast.LtE: '<=',
    ast.Is: '=',
    ast.IsNot: '!=',
    ast.In: 'IN',
    ast.NotIn: 'NI',
    ast.And: 'AND',
    ast.Or: 'OR',
    ast.Not: '!',
}

_NAMES = {
    'file': {
        'name': 'files.name',
        'path': 'files.path',
        'id': 'files.id',
    },
    'tag': {
        'name': 'tags.name',
        'id': 'tags.id'
    }
}


class SelectionBuilder:
    def __init__(self):
        self.result = self._curr = {}

    def _fix_in(self, op, val):
        if op is ast.In or op is ast.NotIn:
            op = ast.Eq if op is ast.In else ast.NotEq
            val = val.elts
        return op, val

    def _build_cmp(self, cmp: ast.Compare):
        v = []
        p = cmp.left

        for op, val in zip(cmp.ops, cmp.comparators):
            op = type(op)
            if op is ast.In or op is ast.NotIn:
                r = [self._build(i) for i in val.elts]

            else:
                r = [self._build(val)]

            v.append({
                'op': _OPS[op],
                'values': [self._build(p)] + r
            })
            p = val

        if len(v) == 1:
            return v[0]

        return {
            'op': 'AND',
            'values': v
        }

    def _build_bool_op(self, cmp: ast.BoolOp):
        return {
            'op': _OPS[type(cmp.op)],
            'values': [self._build(i) for i in cmp.values]
        }

    def _build_str(self, val: ast.Str):
        return {
            'type': 'str',
            'value': val.s,
        }

    def _build_num(self, val: ast.Num):
        return {
            'type': 'number',
            'value': val.n,
        }

    def _build_attr(self, val: ast.Attribute):
        return _NAMES[val.value.id][val.attr]

    def _build(self, val):
        if isinstance(val, ast.BoolOp):
            return self._build_bool_op(val)

        if isinstance(val, ast.Compare):
            return self._build_cmp(val)

        if isinstance(val, ast.Attribute):
            return self._build_attr(val)

        if isinstance(val, ast.Str):
            return self._build_str(val)

        if isinstance(val, ast.Num):
            return self._build_num(val)

        raise ValueError("Unknown or invalid expression")

    def build(self, value):
        if not isinstance(value, ast.Expression):
            raise TypeError("Value must be expression")

        return self._build(value.body)

    def compile(self, v):
        if 'op' in v:
            op = v['op']
            if op == 'IN':
                a = self.compile(v['values'][0])
                return '(%s)' % 'OR'.join(('(%s=%s)' % (a, self.compile(i)) for i in v['values'][1:]))

            if op == 'NI':
                a = self.compile(v['values'][0])
                return '(%s)' % 'AND'.join(('(%s!=%s)' % (a, self.compile(i)) for i in v['values'][1:]))

            return '(%s)' % op.join((self.compile(i) for i in v['values']))
        if 'type' in v:
            return repr(v['value'])
        return v


def compile_selection(sel: str):
    if sel.startswith('sel:'):
        sel = sel[4:]

    b = SelectionBuilder()
    sel = compile(sel, '<selection>', 'eval', ast.PyCF_ONLY_AST, 1)
    return b.compile(b.build(sel))
