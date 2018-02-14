# standard
from collections import OrderedDict, Mapping, MutableMapping, Iterable
import operator
import types
import unittest
# internal
from encyclopedia.templates import Indexed, Unity, Zero

class Relation(Indexed):
    '''
    General purpose, discrete relation container for all four mapping cardinalities:

        - 1:1 (Isomorphism)
        - 1:M (Immersion)
        - M:1 (Function e.g. Python Dictionary)
        - M:M (General Relation)

    Inversion, for all cardinalities, is provided (at the cost of doubled storage)
    '''

    CARDINALITIES = '1:1', '1:M', 'M:1', 'M:M'
    INVERTED_CARDINALITIES = {'1:1': '1:1',
                              '1:M': 'M:1', 'M:1': '1:M', 'M:M': 'M:M'}

    COMPOSITIONS = {
        '1:1': {c: c for c in CARDINALITIES},
        'M:1': {'1:1': 'M:1', 'M:1': 'M:1', '1:M': 'M:M', 'M:M': 'M:M'},
        '1:M': {'1:1': '1:M', '1:M': '1:M', 'M:1': 'M:M', 'M:M': 'M:M'},
        'M:M': {c: 'M:M' for c in CARDINALITIES}}

    unfrozen = Indexed.unfrozen

    def __init__(self,
        init=None, # can start with another dictionary, list or Relation
        cardinality='M:M', # general relation
        ordered=False, # order keys as entered
        frozen=False, # immediately make it immutable?
        ):
        '''
        Create a new Relation using a variety of different inputs
        '''
        if not ordered:
            self.forward = {}
            self.inverse = {}
        elif ordered:
            self.forward = OrderedDict()
            self.inverse = OrderedDict()
        self.ordered = ordered
        self.frozen = frozen

        if cardinality not in Relation.CARDINALITIES:
            raise Relation.Error('Invalid restriction:' + str(cardinality))
        else:
            self.cardinality = cardinality

        if init is None:
            pass
        elif isinstance(init, MutableMapping):
            self.update(init)
        elif isinstance(init, Iterable):
            for item in init:
                assert len(item) == 2
                self[item[0]] = item[1]
        else:
            assert False

    def is_ordered(self):
        return isinstance(self.forward, OrderedDict)

    def __len__(self):
        return len(self.forward)

    def values(self):
        return self.inverse.keys()

    def __iter__(self):
        return self.forward.__iter__()

    def __invert__(self):
        # NOTE: uses references .. not copies
        new = Relation(cardinality=Relation.INVERTED_CARDINALITIES[
                       self.cardinality], ordered=self.ordered)
        new.inverse = self.forward
        new.forward = self.inverse
        return new

    @staticmethod
    def _remove_from(mapping, reference):
        empty = []
        for key, values in mapping.items():
            if reference in values:
                mapping[key].remove(reference)
            if len(mapping[key]) == 0:
                empty.append(key)  # mark for removal
        for e in empty:
            del mapping[e]

    @unfrozen
    def _remove_domain(self, key):
        del self.forward[key]
        Relation._remove_from(self.inverse, key)
    __delitem__ = _remove_domain

    @unfrozen
    def _remove_range(self, key):
        del self.inverse[key]
        Relation._remove_from(self.forward, key)

    @unfrozen
    def __setitem__(self, domain, target):
        # NOTE: Relation using unconventional setitem usage: ADD instead of OVERWRITE
        if self.cardinality in ['1:1', 'M:1']:
            if domain in self.forward:
                self._remove_domain(domain)
        if self.cardinality in ['1:1', '1:M']:
            if target in self.inverse:
                self._remove_range(target)

        if self.ordered:
            self.forward.setdefault(domain, list()).append(target)
            self.inverse.setdefault(target, list()).append(domain)
        else:
            self.forward.setdefault(domain, set()).add(target)
            self.inverse.setdefault(target, set()).add(domain)

    def __getitem__(self, domain):
        if self.cardinality in ['1:1', 'M:1']:
            for target in self.forward[domain]:
                return target
        else:
            return self.forward[domain]

    @staticmethod
    def _get_cardinality(other):
        if isinstance(other, Relation):
            return other.cardinality
        elif isinstance(other, Mapping):
            return 'M:1'
        else:
            return None

    @unfrozen
    def update(self, other):
        cardinality = Relation._get_cardinality(other)
        if cardinality is None:
            raise RelationError('Cannot update:' + str(other))

        for key, value in other.items():
            if cardinality in ['1:1', 'M:1']:
                self[key] = value
            elif cardinality in ['M:M', '1:M']:
                for v in value:
                    self[key] = v
        return self

    @unfrozen
    def subtract(self, other):
        '''
        implement set difference
        '''
        cardinality = Relation._get_cardinality(other)
        if cardinality is None:
            raise RelationError('Cannot remove:' + str(other))
        for key in other:
            del self[key]
        return self

    def compose(self, other):
        '''
        Functional or relational composition
        '''
        if isinstance(other, Relation):
            new = Relation(cardinality=Relation.COMPOSITIONS[
                           self.cardinality][other.cardinality])
            for key in self:
                for middle in self.forward[key]:
                    if middle in other:
                        for value in other.forward[middle]:
                            new[key] = value
        elif isinstance(other, types.FunctionType):
            new = Relation(cardinality=self.cardinality, ordered=self.ordered)
            for key, value in self.items():
                def assign(val):
                    output = other(val)
                    if output is not None:
                        new[key] = output
                if self.cardinality in ['1:1', 'M:1']:
                    assign(value)
                else:
                    for val in value:
                        assign(val)
        elif isinstance(other, Unity):
            new=self.copy()
        else:
            assert False
        return new

    def __str__(self):
        s = []
        s.append('->')
        for d in self.forward:
            s.append(' '.join([str(d), '<', str(self.forward[d])]))
        s.append('<-')
        for ti in self.inverse:
            s.append(' '.join([str(ti), '<', str(self.inverse[ti])]))
        return '\n'.join(s)

    # cross-product operations

    def cross(self, other, op=operator.__or__):
        '''
        Experimental cross-product code ...
        '''
        def setit(x, cardinality):
            if cardinality in ['1:1', 'M:1']:
                return {x}
            elif isinstance(x, list):
                return set(x)
            else:
                return x

        new = Relation()
        for k1, v1 in self.items():
            for k2, v2 in other.items():
                for v3 in op(setit(v1, self.cardinality), setit(v2, other.cardinality)):
                    new[(k1, k2)] = v3
        return new

    class Error(Indexed.Error):
        '''
        Label Relation exceptions
        '''
        pass

# Shortcuts for Relation instantiations

class Isomorphism(Relation):

    def __init__(self, init=None, ordered=False):
        Relation.__init__(self, init, cardinality='1:1', ordered=ordered)


class Function(Relation):

    def __init__(self, init=None, ordered=False):
        Relation.__init__(self, init, cardinality='M:1', ordered=ordered)


class Partition(Relation):

    def __init__(self, init=None, ordered=False):
        Relation.__init__(self, init, cardinality='1:M', ordered=ordered)


class Test_Relation(unittest.TestCase):

    def setUp(self):
        fruit = self.fruit = Relation(ordered=True)
        fruit['apple'] = 'red'
        fruit['apple'] = 'shiny'
        fruit['apple'] = 'round'
        fruit['melon'] = 'round'
        fruit['melon'] = 'green'
        fruit['watermelon'] = 'red'
        fruit['watermelon'] = 'green'
        fruit['watermelon'] = 'ovoid'
        fruit['pear'] = 'yellow'
        fruit['kiwi'] = 'green'
        fruit['kiwi'] = 'seedy'
        self.amount = Isomorphism(
            {'pack': 5, 'bushel': 10, 'crate': 100})
        self.colors = Isomorphism(
            {'red': (1, 0, 0), 'blue': (0, 1, 0), 'green': (0, 0, 1)})

    def test_basic(self):
        fruit = self.fruit
        assert 'seedy' in ~fruit
        assert 'lolipop' not in fruit
        assert fruit.pop('kiwi') == ['green', 'seedy']
        assert 'seedy' not in fruit.values()
        for f in fruit:
            assert isinstance(f, str)
        assert list(fruit.keys()) == ['apple', 'melon', 'watermelon', 'pear']
        assert len(fruit) == 4
        assert len(~fruit) == 6
        assert len(fruit['apple']) == 3
        assert len(fruit['watermelon']) == 3
        assert 'pear' in (~fruit)['yellow']
        assert 'yellow' in fruit['pear']
        assert fruit['pear'] == ['yellow']
        del fruit['pear']
        assert len(fruit) == 3
        assert len(~fruit) == 5
        del fruit['apple']
        assert len(fruit) == 2
        assert len(~fruit) == 4
        another = fruit.copy()
        assert len(~another) == len(~fruit)
        assert len(another) == len(fruit)
        assert len(fruit.keys()) == len(fruit)
        assert len(fruit.values()) == len(~fruit)
        assert len(fruit.items()) == len(fruit)
        assert fruit.get('armadillo') is None
        fruit.clear()
        assert not fruit
        assert fruit.get('melon') is None

    def test_creation(self):
        mi = Isomorphism({'a': 1, 'b': 2, 'c': 11})
        mr = ~mi
        assert mr[2] == 'b'
        mf = Function({'a': 1, 'b': 1, 'c': 11})
        mr = ~mf
        assert mr[1] == {'b', 'a'}
        mp = Partition({'a': 1, 'b': 2, 'c': 11})
        mp['a'] = 3
        mr = ~mp
        assert mr[1] == 'a'
        assert mr[2] != 'a'
        assert mr[3] == 'a'

    def test_update(self):
        fruits = {'apple': 'red', 'cherry': 'red',
                  'strawberry': 'red', 'banana': 'yellow'}
        fruit = Relation(fruits)
        assert len(fruit) == len(fruits)
        more = {'yellow': 'pear', 'pomegranate': 'red', 'watermelon': 'seedy'}
        fruit.update(more)
        assert len(fruit) == len(more) + len(fruits)
        even_more = Isomorphism({'papaya': 'starchy', 'grape': 'tangy'})
        fruit.update(even_more)
        assert len(fruit) == len(even_more) + len(more) + len(fruits)

    def test_restrictions(self):
        '''
        Attack the underpinnings directly
        NOTE: not suggested usage as this can make the Relations inconsistent/corrupt
        '''
        fruit = Relation(cardinality='1:1')
        fruit['apple'] = 'red'
        fruit['pear'] = 'yellow'
        fruit['apple'] = 'green'
        assert 'apple' in fruit
        fruit['watermelon'] = 'green'
        assert 'apple' not in fruit
        fruit['papaya'] = 'green'
        assert 'watermelon' not in fruit

        fruit.cardinality = 'M:1'
        fruit['papaya'] = 'green'
        fruit['raspberry'] = 'blue'
        fruit['raspberry'] = 'red'
        assert fruit['raspberry'] == 'red'
        fruit['cranberry'] = 'red'
        assert 'raspberry' in fruit
        assert fruit['raspberry'] == 'red'

        fruit.cardinality = '1:M'
        fruit['cranberry'] = 'round'
        fruit['lemon'] = 'sour'
        fruit['cranberry'] = 'sour'
        assert 'lemon' not in fruit
        assert len(fruit['cranberry']) > 1
        fruit['pear'] = 'sweet'

        fruit.cardinality = 'M:M'
        fruit['apple'] = 'sweet'
        assert len(fruit['apple']) == 1
        fruit['apple'] = 'fruit'
        assert len(fruit['apple']) == 2

    def test_composition(self):
        fruit = Function()
        fruit['apple'] = 'red'
        fruit['pear'] = 'yellow'
        colors = Isomorphism()
        colors['yellow'] = '0:1:1'
        colors['red'] = '1:0:0'
        assert (fruit * colors).cardinality == 'M:1'
        assert Isomorphism(fruit * colors).cardinality == '1:1'
        properties = Relation()
        properties['red'] = 'sanguine'
        properties['red'] = 'pinkish'
        properties['red'] = 'bloody'
        assert len(fruit * properties) == 1
        assert len(properties * fruit) == 0

    def test_arithmetic(self):
        colors = Isomorphism()
        colors['yellow'] = '0:1:1'
        colors['red'] = '1:0:0'
        fruit = Isomorphism()
        fruit['apple'] = 'red'
        fruit['pear'] = 'yellow'
        funny = fruit + colors
        assert len(funny) == len(fruit) + len(colors)
        funny -= colors
        assert funny == fruit

    def test_freeze(self):
        f0 = self.fruit
        f1 = f0.copy()
        f1['something'] = 'else'
        assert 'something' in f1
        assert f1 != f0
        del f1['apple']
        assert 'apple' not in f1
        f2 = self.fruit.freeze()
        f2['something'] = 'else'
        assert f2 == f0
        del f2['apple']
        assert 'apple' in f2

    def test_cross_product(self):
        fruit = self.fruit
        colors = self.colors
        assert len(fruit.cross(colors)) == len(fruit) * len(colors)

    def test_union(self):
        '''
        Examine different ways of combining Relations
        '''
        fruit = self.fruit
        colors = self.colors
        added = fruit + colors
        assert len(added) == len(fruit) + len(colors)
        assert isinstance(added, Relation)
        unpacked = {**fruit, **colors}
        assert len(unpacked) == len(fruit) + len(colors)
        assert isinstance(unpacked, dict)
        updated = fruit.copy().update(colors)
        assert len(updated) == len(fruit) + len(colors)
        assert updated == added
        assert updated != unpacked

    def test_pipe(self):
        fruit = self.fruit
        new = fruit * (lambda x: x + '1') * (lambda x: x.upper())
        assert len(new) == len(fruit)
        new = (~fruit) * (lambda x: x + '1') * (lambda x: x.upper())
        assert len(new) == len(~fruit)
        new = fruit * \
            (lambda x: x if x not in ['shiny', 'red', 'round'] else None)
        assert 'apple' not in new
        new = fruit * (lambda x: x if x in ['shiny', 'red', 'round'] else None)
        assert 'kiwi' not in new
        assert 'apple' in new

    def test_zero(self):
        fruit = self.fruit
        more = fruit+Zero()
        for key in fruit:
            assert more[key] == fruit[key]

    def test_unity(self):
        unity = Unity()
        fruit = self.fruit
        assert len(fruit*unity) == len(fruit)
        back = fruit * ~fruit # not identity, but kind of
        for key in back:
            assert key in back[key]

        more = Relation(cardinality='1:M')
        more.update(fruit)
        identity = more * ~more  # identity
        for key in identity:
            assert key == key

if __name__ == '__main__':
    unittest.main()
