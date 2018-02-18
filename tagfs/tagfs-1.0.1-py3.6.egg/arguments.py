import builtins
import functools
import inspect
import sys
import typing


class ArgumentParser:
    FIRST_LINES = (
        'Usage: {program} COMMAND ARGS...',
        'Where command is:'
    )

    def __init__(self, *, types=None, help_text='', add_first_line=True, init_type=None):
        self._help = help_text.splitlines(False)
        self._args = []

        if add_first_line:
            self._help = list(self.FIRST_LINES) + self._help

        if types is not None:
            self.add_types(types, init_type=init_type)

    def add(self, pattern, typ, *, init_type=None):
        if init_type is None:
            init_type = typ

        obj = getattr(typ, pattern[-1])
        new = self._get_type_init(init_type)
        self._args.append((pattern, init_type, new, obj))
        x = ' '.join((new.__code__.co_varnames[i + 1].upper() for i in range(new.__code__.co_argcount - 1))) + ' '\
            + ' '.join(pattern) + ' '\
            + ' '.join((obj.__code__.co_varnames[i + 1].upper() for i in range(obj.__code__.co_argcount - 1)))
        self._help.append('  {:<23.23} {}'.format(x, self._get_doc(obj)))

    def add_type(self, typ, *, prefix=(), init_type=None):
        for mn in dir(typ):
            if not mn.startswith('_') and callable(getattr(typ, mn)):
                self.add((*prefix, mn), typ, init_type=init_type)

    def add_types(self, types, *, prefix=(), init_type=None):
        for name, typ in types.items():
            self.add_type(typ, prefix=prefix + (name, ), init_type=init_type)

    def print_help(self, program, error=False):
        v = '\n'.join(self._help).format(program=program)
        if error:
            print(v, file=sys.stderr)
        else:
            print(v)

    def parse(self, args):
        args = list(args)
        program = args.pop(0)

        if not args:
            self.print_help(program, True)
            return False

        for pattern, typ, new, obj in self._args:
            bl = new.__code__.co_argcount - 1
            al = obj.__code__.co_argcount - 1

            if len(pattern) + al + bl != len(args):
                continue

            for i, v in enumerate(pattern):
                if args[i + bl] != v:
                    break
            else:
                argv = []
                lp = len(pattern) + bl

                for i in range(bl):
                    argv.append(self._convert_arg(new, i, args[i]))

                v = typ(*argv)
                argv = []

                for i in range(al):
                    argv.append(self._convert_arg(obj, i, args[i + lp]))

                v = self._getattr_long(v, *pattern)(*argv)
                if v is not None:
                    print(v)
                return True

        self.print_help(program, True)
        return False

    @staticmethod
    def _getattr_long(obj, *args):
        for i in args:
            obj = getattr(obj, i)
        return obj

    @staticmethod
    def _get_doc(v):
        v = getattr(v, '__doc__', None)
        if v is not None:
            v = v.strip()

        if not v:
            return 'Undocumented'
        return v.splitlines()[0]

    @staticmethod
    def _convert_arg(method, arg_no, val: str, exc_type=None):
        start = 0
        i = -1

        while True:
            li = i
            i = val.find(':', start)
            if i == -1:
                break

            if i + 1 != len(val) and val[i + 1] == ':':
                val = val[:i] + val[i + 1:]
                start = i + 1
                i = -1
            else:
                start = i + 1

        if li != -1:
            return getattr(builtins, val[li + 1:])(val[:li])

        if exc_type is None:
            typ = method.__annotations__.get(method.__code__.co_varnames[arg_no + 1])
            if typ is None:
                return val

        else:
            typ = exc_type

        # noinspection PyUnresolvedReferences,PyProtectedMember
        if isinstance(typ, typing._Union):
            for i in typ.__args__:
                try:
                    return i(val)
                except TypeError:
                    pass
                except ValueError:
                    pass

        elif issubclass(typ, typing.List):
            # noinspection PyUnresolvedReferences
            item_type = typ.__args__[0]
            return [ArgumentParser._convert_arg(method, arg_no, item, item_type)
                    for item in val.split(',')]

        if callable(typ):
            try:
                return typ(val)
            except TypeError:
                pass
            except ValueError:
                pass
        return val

    @staticmethod
    def _get_type_init(typ):
        i = getattr(typ, '__init__', None)
        if hasattr(i, '__code__'):
            return i
        i = getattr(typ, '__new__', None)
        if hasattr(i, '__code__'):
            return i
        raise TypeError("'__init__' and '__new__' for type %r is native!" % typ.__name__)


def function_wrapper(func=None, *, name=None):
    if func is not None:
        return _function_wrapper(func.__name__, func)
    return functools.partial(_function_wrapper, name)


def _function_wrapper(name, func):
    name = name.split('.')
    mod = func.__module__
    init = _init_none
    func = func0 = _make_fn(func, name[-1], mod)

    if len(name) == 1:
        return type(name[0], (), {
            name[0]: func,
            '__module__': mod,
            '__init__': init
        })

    for i in reversed(name[1:]):
        func = type(i, (), {
            i: func,
            '__module__': mod,
            '__init__': init
        })()

    return type(name[0], (), {
        name[0]: func,
        name[-1]: func0,
        '__module__': mod,
        '__init__': init
    })


def _init_none(self):
    pass


def _make_fn(fn, name, mod):
    s = inspect.signature(fn, follow_wrapped=False)
    pn = []

    for i, v in s.parameters.items():
        if v.kind is inspect.Parameter.KEYWORD_ONLY:
            if v.default is inspect.Parameter.empty:
                raise ValueError("Can't wrap function with non-default keyword-only arguments")
            i = '{0}={0}'.format(i)
        pn.append(i)

    c = 'def %s(self, %s:\n    return __fn__(%s)' % (name, str(s)[1:], ', '.join(pn))
    g = {'__fn__': fn}
    exec(c, g, g)
    f = g[name]
    f.__doc__ = fn.__doc__
    f.__module__ = mod
    return f
