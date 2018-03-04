"""a module that contains testcode for pyexpander.py

"""
import sys
from pyexpander.lib import *

def test_processToPrint():
    r'''Test function processToList from pyexpander.py:
    >>> gbls= processToPrint(parseString(r"""$py(x=12)abc$(x)def"""))
    abc12def
    >>> gbls= processToPrint(parseString(r"""$py(x="XY")abc$(x)def"""))
    abcXYdef
    >>> gbls= processToPrint(parseString(r"""$py(x=12;y=3)abc$(x*y)def"""))
    abc36def
    >>> gbls= processToPrint(parseString(r"""$py(x=")";y="(")abc$(x)$(y)def"""))
    abc)(def

    Test for nobracket vars:
    >>> gbls= processToPrint(allow_nobracket_vars=True,
    ...                      parse_list=parseString(r"""
    ... $py(a=1)\
    ... a with brackets: $(a)
    ... a without brackets: $a some text follows here
    ... """))
    <BLANKLINE>
    a with brackets: 1
    a without brackets: 1 some text follows here

    Test if-then-else-endif, condition is True:
    >>> gbls= processToPrint(parseString(r"""
    ... $py(x=True)
    ... some text
    ... $if(x)
    ... x is True
    ... $else
    ... x is False
    ... $endif
    ... continued text
    ... """))
    <BLANKLINE>
    <BLANKLINE>
    some text
    <BLANKLINE>
    x is True
    <BLANKLINE>
    continued text

    Test if-then-else-endif, condition is False:
    >>> gbls= processToPrint(parseString(r"""
    ... $py(x=False)
    ... some text
    ... $if(x)
    ... x is True
    ... $else
    ... x is False
    ... $endif
    ... continued text
    ... """))
    <BLANKLINE>
    <BLANKLINE>
    some text
    <BLANKLINE>
    x is False
    <BLANKLINE>
    continued text

    Test if-then-else-endif, condition is False with continued lines:
    >>> gbls= processToPrint(parseString(r"""
    ... $py(x=False)\
    ... some text
    ... $if(x)\
    ... x is True
    ... $else\
    ... x is False
    ... $endif\
    ... continued text
    ... """))
    <BLANKLINE>
    some text
    x is False
    continued text

    Test if-then-elif-else-endif:
    >>> gbls= processToPrint(parseString(r"""
    ... $py(x=3)\
    ... now test x
    ... $if(x==0)\
    ... x is 0
    ... $elif(x==1)\
    ... x is 1
    ... $elif(x==3)\
    ... x is 3
    ... $endif\
    ... """))
    <BLANKLINE>
    now test x
    x is 3

    Test if-then-elif-else-endif, if-part matches:
    >>> gbls= processToPrint(parseString(r"""
    ... $py(x=0)\
    ... now test x
    ... $if(x==0)\
    ... x is 0
    ... $elif(x==1)\
    ... x is 1
    ... $else\
    ... x has an unexpected value
    ... $endif\
    ... """))
    <BLANKLINE>
    now test x
    x is 0

    Test if-then-elif-else-endif, else-part matches:
    >>> gbls= processToPrint(parseString(r"""
    ... $py(x=-1)\
    ... now test x
    ... $if(x==0)\
    ... x is 0
    ... $elif(x==1)\
    ... x is 1
    ... $else\
    ... x has an unexpected value
    ... $endif\
    ... """))
    <BLANKLINE>
    now test x
    x has an unexpected value

    Test begin-end
    >>> gbls= processToPrint(parseString(r"""
    ... $py(a=1)\
    ... a here:$(a)
    ... $begin\
    ... $py(a=2)\
    ... a within block:$(a)
    ... $end\
    ... a outside of block:$(a)
    ... """))
    <BLANKLINE>
    a here:1
    a within block:2
    a outside of block:1

    test global statement:
    >>> gbls= processToPrint(parseString(r"""
    ... $py(a=1;b=1)\
    ... a:$(a) b:$(b)
    ... $begin\
    ... $nonlocal(a)\
    ... $py(a=2;b=2)\
    ... now a:$(a) b:$(b)
    ... $end\
    ... and now a:$(a) b:$(b)
    ... """))
    <BLANKLINE>
    a:1 b:1
    now a:2 b:2
    and now a:2 b:1

    Test global statement, a more complicated example:
    >>> gbls= processToPrint(parseString(r"""
    ... $py(a=1;b=10)\
    ... a:$(a) b:$(b)
    ... $begin\
    ... $nonlocal(a,b)\
    ... $py(a=2;b=20)\
    ... now a:$(a) b:$(b)
    ... $begin\
    ... $nonlocal(a)\
    ... $py(a=3;b=30)\
    ... now a:$(a) b:$(b)
    ... $end\
    ... after inner block: a:$(a) b:$(b)
    ... $end\
    ... after outer block: a:$(a) b:$(b)
    ... """))
    <BLANKLINE>
    a:1 b:10
    now a:2 b:20
    now a:3 b:30
    after inner block: a:3 b:20
    after outer block: a:3 b:20

    Test default statement, first the case of an undefined variable:
    >>> gbls= processToPrint(parseString(r"""
    ... undefined variable: $(a)
    ... """))
    Traceback (most recent call last):
        ...
    NameError: name 'a' is not defined at line 2, col 23

    Now use the default statement to pre-define variables:
    >>> gbls= processToPrint(parseString(r"""
    ... $py(b=200)\
    ... $default(a=1, b=2)\
    ... a: $(a) b: $(b)
    ... """))
    <BLANKLINE>
    a: 1 b: 200

    Test while:
    >>> gbls= processToPrint(parseString(r"""
    ... $py(a=4)\
    ... $while(a>0)\
    ... a now: $(a)
    ... $py(a=a-1)\
    ... $endwhile\
    ... """))
    <BLANKLINE>
    a now: 4
    a now: 3
    a now: 2
    a now: 1

    test for:
    >>> gbls= processToPrint(parseString(r"""
    ... $for(x in range(3,5))\
    ... x:$(x)
    ... $endfor\
    ... """))
    <BLANKLINE>
    x:3
    x:4

    Test for_begin:
    >>> gbls= processToPrint(parseString(r"""
    ... $py(a=1)\
    ... $for_begin(x in range(3,5))\
    ... x:$(x) a:$(a)
    ... $py(a=a*10)\
    ... $endfor\
    ... after loop a:$(a)
    ... """))
    <BLANKLINE>
    x:3 a:1
    x:4 a:10
    after loop a:1

    test include:
    >>> import os
    >>> f=open("test","w")
    >>> l=f.write("""in-include-file
    ... a is now: $(a)
    ... increment a by one $py(a=a+1)
    ... end-of-include-file
    ... """)
    >>> f.close()
    >>> gbls= processToPrint(parseString(r"""
    ... $py(a=1)\
    ... a now: $(a)
    ... $include("test")\
    ... a after include: $(a)
    ... """))
    <BLANKLINE>
    a now: 1
    in-include-file
    a is now: 1
    increment a by one 
    end-of-include-file
    a after include: 2
    >>> os.remove("test")

    >>> gbls= processToPrint(parseString(r"""
    ... Test extend
    ... $py(a=10)\
    ... $py(
    ... def plusone(x):
    ...     return x+1
    ...    )\
    ... $extend(a,plusone)
    ... Now we can use a directly: $a
    ... and we can use plusone directly: $plusone(19)
    ... """))
    <BLANKLINE>
    Test extend
    <BLANKLINE>
    Now we can use a directly: 10
    and we can use plusone directly: 20
    '''
    pass

def _test():
    import doctest
    sys.stdout.write("testing...\n")
    doctest.testmod()
    sys.stdout.write("done\n")

if __name__ == "__main__":
    _test()
