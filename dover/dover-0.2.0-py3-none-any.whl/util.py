from itertools import chain, repeat


def append(seq, starting, fmt='{{: <{}}} '):
    format = None
    if isinstance(fmt, (list, tuple)):
        format = fmt
    else:
        format = list(repeat(fmt, len(seq)))

    for i, s in enumerate(seq):
        starting += format[i].format(s)
    return starting


def find_column_widths(*args):
    return [max([len(str(z[i]).strip()) for z in chain(*args)])
        for i in range(0, max([len(x) for x in chain(*args)]))]


def make_format_str(indent, *args, format=None):
    columns = find_column_widths(*args)
    indent_str = ' ' * indent
    if format is not None: 
        return append(columns, indent_str, fmt=format)
    return append(columns, indent_str)


def format_seqs(*args, indent=4, format=None):
    fmt_str = make_format_str(indent, *args, format=format) 
    for arg in chain(*args):
        yield fmt_str.format(*arg)
