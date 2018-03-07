#!/usr/bin/env python
#
# test_cache.py -
#
# Author: Paul McCarthy <pauldmccarthy@gmail.com>
#


import              gc
import itertools as it

import fsleyes_props as props

import pytest


class MyObj(props.HasProperties):
    myint  = props.Int()
    mybool = props.Boolean(default=False)
    mystr  = props.String()


def test_PropCache():


    count  = [0]
    target = MyObj()

    def keyfunc():
        key = count[0]
        count[0] += 1
        return key

    # values that the target properties
    # will take. The first ones are the
    # initial values
    values = {
        'myint'  : [3, 5, 9],
        'mybool' : [True, False, True],
        'mystr'  : ['abc', '123', 'ABC']
    }

    triggers = [(MyObj(), 'myint'),
                (MyObj(), 'mybool')]

    cache = props.PropCache(
        target,
        ['myint', 'mybool', 'mystr'],
        keyfunc,
        triggers)

    target.myint  = values['myint'][ 0]
    target.mybool = values['mybool'][0]
    target.mystr  = values['mystr'][ 0]

    with pytest.raises(ValueError):
        cache.get(0, 'myint', 'a', 'b')

    # if no values cached, should
    # return the current value
    assert cache.get(999, 'myint')  == values['myint'][ 0]
    assert cache.get(999, 'mybool') == values['mybool'][0]
    assert cache.get(999, 'mystr')  == values['mystr'][ 0]

    # Or a default value if we provide one
    assert cache.get(999, 'myint',  'blabs') == 'blabs'
    assert cache.get(999, 'mybool', 'blabs') == 'blabs'
    assert cache.get(999, 'mystr',  'blabs') == 'blabs'

    # trigger the cache
    triggers[0][0].myint = 99

    # change the current values
    target.myint  = values['myint'][ 1]
    target.mybool = values['mybool'][1]
    target.mystr  = values['mystr'][ 1]

    # check the cache
    assert cache.get(0, 'myint')  == values['myint'][ 0]
    assert cache.get(0, 'mybool') == values['mybool'][0]
    assert cache.get(0, 'mystr')  == values['mystr'][ 0]

    # trigger the cache again
    triggers[1][0].mybool = True

    # change the current values
    target.myint  = values['myint'][ 2]
    target.mybool = values['mybool'][2]
    target.mystr  = values['mystr'][ 2]

    # check the cache
    for i in range(2):

        assert cache.get(i, 'myint')  == values['myint'][ i]
        assert cache.get(i, 'mybool') == values['mybool'][i]
        assert cache.get(i, 'mystr')  == values['mystr'][ i]


def test_PropCache_gc():

    clearThings = ['target', 'keyfunc']

    for clearThing in clearThings:
        _test_PropCache_gc(clearThing)


def _test_PropCache_gc(clearThing):

    count  = [0]
    target = MyObj()

    def keyfunc():
        key = count[0]
        count[0] += 1
        return key

    triggers = [(MyObj(), 'myint'),
                (MyObj(), 'mybool')]

    cache = props.PropCache(target,
                            ['myint',
                             'mybool',
                             'mystr'],
                            keyfunc,
                            triggers)

    target.myint  = 5
    target.mybool = True
    target.mystr  = 'abc'

    # Put something in the cache
    triggers[0][0].myint = 99

    target.myint  = 99
    target.mybool = False
    target.mystr  = '123'

    assert cache.get(0, 'myint')  == 5
    assert cache.get(0, 'mybool') is True
    assert cache.get(0, 'mystr')  == 'abc'

    # GC the keyfunc or the target
    if   clearThing == 'target':  del target
    elif clearThing == 'keyfunc': del keyfunc

    gc.enable()
    gc.collect()

    # Test cache retrieval or triggering
    if clearThing == 'target':
        assert not cache.alive()
        with pytest.raises(props.CacheError):
            print(cache.get(0, 'myint'))


    elif clearThing == 'keyfunc':
        triggers[1][0].mybool = True
        assert not cache.alive()
        with pytest.raises(props.CacheError):
            print(cache.get(0, 'myint'))
