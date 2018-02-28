#!/usr/bin/python

def remove_magics(raw_text):
    """Removes cell magic from .py created from .ipynb"""
    new_lines = []
    for line in raw_text.split('\n'):
        if line.startswith('get_ipython().run_cell_magic'):
            contents = eval(line.replace('get_ipython().run_cell_magic', ''))
            assert len(contents) == 3
            new_lines.append('### start get_ipython().run_cell_magic')
            new_lines.append('### %%'+contents[0])
            new_lines.append('### '+contents[1])
            for item in contents[2].split('\n'):
                new_lines.append(item)
            new_lines.append('### end get_ipython().run_cell_magic')
        elif line.startswith('get_ipython().magic('):
            contents = eval(line.replace('get_ipython().magic', ''))
            new_lines.append('### get_ipython().magic')
            new_lines.append('### %'+contents)
            if contents.startswith('aimport'):
                new_lines.append(contents[1:]+'  ### from magic')
        else:
            new_lines.append(line)
    return '\n'.join(new_lines)

def print79():
    """Prints text representation of maximum 79 char code width.
    One could always use textwrap.wrap instead"""
    print('1234567-101234567-201234567-301234567-401234567-501234567-601234567-70123456789')


def wrap(text, maxlength=80, insert='\n'):
    """Returns text with 'insert' added in place of whitespace
    closest to position of maxlength every iteration, e.g. every line. """
    text = str(text)
    linelength = 0
    newtext = [[]]
    i = 0 # position in line
    for j, word in enumerate(text.split(' ')):
        nextlinelength = linelength + len(word)
        if j != 0:
            nextlinelength += 1 #for the space
        if nextlinelength >= maxlength:
            newtext.append([word])
            i += 1
            linelength = len(word)
        else:
            newtext[i].append(word)
            linelength = nextlinelength
    output = []
    for line in newtext:
        output.append(' '.join(line))
    return insert.join(output)

def simple_table(list_of_lists, first_is_header=False):
    length = len(list_of_lists[0])
    maxlens = [0] * length
    for row in list_of_lists:
        for i, item in enumerate(row):
            maxlens[i] = max(maxlens[i], len(str(item)))

    if first_is_header:
        sep_row = ['+']
        for maxlen in maxlens:
            sep_row.append('-'*(maxlen+2))
            sep_row.append('+')

    for rownum, row in enumerate(list_of_lists):
        output = ['| ']
        for i, (item, maxlen) in enumerate(zip(row, maxlens)):
            output.append(str(item))
            output.append(' '*(maxlen+1-len(str(item))))
            if i < length:
                output.append('| ')
            else:
                output.append('|')
        print(''.join(output))
        if first_is_header and rownum == 0:
            print(''.join(sep_row))

def niceprint(obj, width=80, objname='', align=True):
    """Prints single-level list or dict in PEP8 compliant yet compact
    format. If value given for objname, prints it at beginning; if
    align is True, aligns new line to length of objname."""
    result = []
    pos = 0
    if len(objname) > 0:
        result.append(objname+" = ")
        pos += len(objname+" = {")
        if align:
            indent = len(objname) + 4
        else:
            indent = 4
    else:
        indent = 1
    pos += indent
    remaining = len(obj)
    if type(obj) == dict:
        result.append("{")
        keys = list(obj.keys())
        try:
            keys.sort()
        except:
            pass
        for k in keys:
            v = obj[k]
            if type(k) == str:
                if k.find("'") != -1:
                    quotechar = "\""
                else:
                    quotechar = "'"
                k_ = k.replace("\"", "\\\"")
                k_ = quotechar+k_+quotechar
            else:
                k_ = k
            if type(v) == str:
                if v.find("'") != -1:
                    quotechar = "\""
                else:
                    quotechar = "'"
                v_ = v.replace("\"", "\\\"")
                v_ = quotechar+v_+quotechar
            else:
                v_ = v
            remaining -= 1
            if remaining > 0:
                newitem = "{}: {}, ".format(k_, v_)
            else:
                newitem = "{}: {}}}".format(k_, v_)
            newlen = len(newitem)
            if pos + newlen > width:
                result.append('\n')
                result.append(' '*indent)
                pos = indent
            result.append(newitem)
            pos += newlen
    elif type(obj) == list:
        result.append('[')
        for item in obj:
            if type(item) == str:
                if item.find("'") != -1:
                    quotechar = "\""
                else:
                    quotechar = "'"
                item_ = item.replace("\"", "\\\"")
                item_ = quotechar+item_+quotechar
            else:
                item_ = item
            remaining -= 1
            if remaining > 0:
                newitem = "{}, ".format(item_)
            else:
                newitem = "{}]".format(item_)
            newlen = len(newitem)
            if pos + newlen > width:
                result.append('\n')
                result.append(' '*indent)
                pos = indent
            result.append(newitem)
            pos += newlen
    elif type(obj) == set:
        result.append('{')
        items = list(obj)
        try:
            items.sort()
        except:
            pass
        for item in items:
            if type(item) == str:
                if item.find("'") != -1:
                    quotechar = "\""
                else:
                    quotechar = "'"
                item_ = item.replace("\"", "\\\"")
                item_ = quotechar+item_+quotechar
            else:
                item_ = item
            remaining -= 1
            if remaining > 0:
                newitem = "{}, ".format(item_)
            else:
                newitem = "{}}}".format(item_)
            newlen = len(newitem)
            if pos + newlen > width:
                result.append('\n')
                result.append(' '*indent)
                pos = indent
            result.append(newitem)
            pos += newlen
    if type(obj) == dict or type(obj) == list or type(obj) == set:
        print(''.join(result))
