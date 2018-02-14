# standard
import unittest
import hashlib
import types
# internal
from encyclopedia.templates import Unindexed
from encyclopedia.relate import Relation

class Forest(Unindexed):
    '''
    An Encyclopedia of [trees](https://en.wikipedia.org/wiki/Tree_(graph_theory)#Forest)

    Note that there is no specific "Tree" class; instead, a Tree is Forest with a single
    connected (tree) graph.  This is purposeful as adding two Trees creates a Forest, not another Tree.

    Terminology for this class:

    - Tree: single, connected (tree) graph
    - Forest: a (possibly empty) collection of Trees, supporting Unindexed Encyclopedia operations
    - Node: a single node in a graph
    - Twig: a connected pair of nodes
    - Sprout: a new, connected node

    '''
    def __init__(self,
        offset:int = 0, # starting node counter
        parent = None):# for future use ...
        '''
        Create the forest
        '''
        self.trees = set() # *disconnected* set of tree graphs
        self.aliases = Relation(cardinality='1:M') # alias -> node(s)
        self.nodes = Relation(cardinality='1:M') # node -> upper node(s)
        self.levels = Relation(cardinality='M:1') # node(s) -> level
        self.counter = offset # counter used for creating unique Node IDs
        self.parent = parent # future use for referencing originating forest (where applicable)
        self.frozen = False # start off mutable

    unfrozen = Unindexed.unfrozen

    def __iter__(self):
        '''
        Notes: creates Forest.keys() via mixin
        '''
        yield from self.aliases.keys()

    def __contains__(self, alias):
        '''
        Implicit by __getitem__ (mixin) but implemented for performance reasons
        '''
        if isinstance(alias, Forest.Node):
            return alias in self.aliases.values()
        else:
            return alias in self.aliases

    def values(self):
        '''
        Implicit by __getitem__ (mixin) but implemented for performance reasons
        '''
        return self.aliases.values()

    def __len__(self):
        '''
        Note: number of keys (i.e. aliases) may be *less than* number of values (i.e. nodes)
        '''
        return len(self.aliases.values())

    def canopy(self):
        return (self.nodes.values() | self.trees) - self.nodes.keys()

    def height(self):
        '''
        Maximum height (of all nodes in Forest)
        '''
        return max(self.levels.values())

    def __str__(self):
        return '\n'.join([str(self.trees), str(self.nodes)])

    class Node():
        '''
        Store the (non-unique) alias and its (unique) ID for a Node
        '''
        def __init__(self, alias, id):
            self.alias = Forest.Node.deid(alias)
            self.id = id

        @staticmethod
        def deid(alias):
            return alias.alias if isinstance(alias, Forest.Node) else alias

        def offset(self, value):
            return Forest.Node(self.alias, self.id+value)

        def __hash__(self):
            return self.id

        def __lt__(self, other):
            return self.id < other.id

        def __eq__(self, other):
            return self.id == other.id

        def __str__(self):
            return '#' + str(self.id) + ':' + str(self.alias)

        def __repr__(self):
            return str(self)

        def identified(self,
                identified: bool, # return fullNode
                off: int=0,
            ):
            '''
            Return either an offset Node ID or simply the alias
            '''
            return self.offset(off) if identified else self.alias

    def sprout(self, alias):
        '''
        Make a unique node identifier referenced by an alias
        '''
        self.counter += 1
        return Forest.Node(alias, self.counter)

    def aliased(self, alias=None):
        '''
        Generate set of nodes referenced by alias
        '''
        for alias in self.trees if alias is None else {alias}:
            if isinstance(alias, Forest.Node):
                nodes = {alias} # single node
            elif alias in self.aliases:
                nodes = self.aliases[alias] # multiple nodes, maybe
            else:
                raise KeyError
            yield from nodes

    def above(self,
            alias, # start here
            aliased = False, # return just alias
            ):
        '''
        Generate nodes above node(s)
        '''
        for node in self.aliased(alias):
            if node in self.nodes:
                for other in self.nodes[node]:
                    yield other.alias if aliased else other

    def branches(self, alias):
        '''
        Return branches (e.g. Trees) above the node(s)
        '''
        for node in self.above(alias):
            yield self[node]

    def below(self,
        alias, # start here
        aliased = False, # return just alias
        ):
        '''
        Generate parent below node(s)
        '''
        for node in self.aliased(alias):
            if node in ~self.nodes:
                next = (~self.nodes)[node]
                yield next.alias if aliased else next

    def root(self, alias=None):
        '''
        Return tree root of node(s)
        '''
        for node in self.aliased(alias):
            if node in self.trees:
                yield node
            else:
                for lower in self.below(node):
                    yield from self.root(lower)

    def leaves(self, alias=None):
        '''
        Return leaves reachable from  alias
        '''
        for node in self.aliased(alias):
            if node not in self.nodes:
                yield node
            else:
                for upper in self.above(node):
                    yield from self.leaves(upper)

    def _add_node(self, alias):
        if isinstance(alias, Forest.Node): # already sprouted
            new = alias
            if alias.id > self.counter: # pre-offset
                self.counter = alias.id + 1
        else:
            new = self.sprout(alias)
        self.aliases[Forest.Node.deid(new)] = new
        return new

    def _add_twig(self, lower, upper):
        for node in self.aliased(lower):
            new = self._add_node(upper)
            self.nodes[node] = new
            self.levels[new] = self.levels[node]+1

    def _add_tree(self, tree):
        new = self._add_node(tree)
        self.trees.add(new)
        self.levels[new] = 0
        return new

    def climb(self,
            alias = None, # start here; when None start at tree roots
            level: bool = False, # include level in iterator
            twig: bool = False, # return connective (lower, upper) pair instead of just node
            identified: bool = True, # when True use full Node ID, when False just use aliases
            offset: int = 0, # add offset to node ID
        ):
        '''
        Generate tree of nodes reacheable from alias
        '''
        def idd(node):
            '''
            Just a shortcut, meaning: "Id'd"
            '''
            return node.identified(identified, offset)

        def token(lower, upper=None):
            if level:
                height = (self.levels[node],)
            else:
                height = ()
            if upper is None:
                return height + (idd(lower),)
            else:
                return height + (idd(lower), idd(upper))

        for node in self.aliased(alias):
            if not twig:
                yield token(node)
            if node in self.nodes:
                for other in self.nodes[node]:
                    if twig:
                        yield token(node, other)
                    yield from self.climb(other,
                        level = level,
                        twig = twig,
                        offset = offset,
                        identified = identified)
    def sorted(self,
            alias = None,
            level: bool = False,
            twig: bool = False,
            offset: int = 0,
            identified: bool = True,
            aliased: bool = False, # return just alias
        ):
        '''
        A topologically sorted node *list* (not iterator)
        '''
        nodes = list(
            self.climb(alias,
                level = True, # need this to topologically sort
                offset = offset,
                identified = identified,
                twig = twig))
        if not level: # get rid of the level if not requested
            if twig:
                nodes = [(lower, upper) for lvl, lower, upper in nodes]
            else:
                nodes = [node for lvl, node in nodes]
        nodes = sorted(nodes)
        if aliased:
            return [node.alias for node in nodes]
        else:
            return nodes

    @unfrozen
    def __delitem__(self, node):
        for node in reversed(self.sorted(node, level=False)):
            del self.levels[node]
            del (~self.aliases)[node]
            if node in self.nodes:
                del self.nodes[node]
            if node in self.trees:
                self.trees.remove(node)
            else: # has a parent
                del (~self.nodes)[node]

    @staticmethod
    def equals(forest1, forest2, tree1=None, tree2=None):
        def nodes(forest, tree):
            return forest.sorted(alias=tree, identified=False, level=True, twig=True)
        return nodes(forest1, tree1) == nodes(forest2, tree2)

    def __eq__(self, other):
        return Forest.equals(self, other)

    def cutting(self,
            alias = None,
            identified: bool = True,
            offset: int = 0,
            morph: types.FunctionType = Unindexed.identity, # modify keys/values upon entry
        ):
        '''
        Return subforest rooted at alias
        '''
        def morphed(node):
            if isinstance(node, Forest.Node):
                alias = morph(node.alias)
                return Forest.Node(alias,node.id) if alias is not None else None
            else:
                return morph(node)

        new = self.__class__(parent=self, offset=offset)
        for node in self.aliased(alias):
            tree = morphed(node.identified(identified, offset))
            if tree is not None:
                new._add_tree(tree)
                for lower, upper in self.climb(
                        node,
                        level=False,
                        identified=identified,
                        offset=offset,
                        twig=True):
                    lower, upper = morphed(lower), morphed(upper)
                    if lower is not None and upper is not None and lower in new:
                        new[lower] = upper
        return new

    def limb(self,
            alias,
            offset: int = 0
        ):
        '''
        Return the tree (single line of nodes) below node(s)
        '''
        def gravity(node):
            yield node
            for down in self.below(node):
                yield from gravity(down)

        new = self.__class__(parent=self, offset=offset)
        for node in self.aliased(alias):
            nodes = list(gravity(node))
            nodes.reverse()
            new += nodes[0] # the tree root
            for i,node in enumerate(nodes[1:]):
                new[nodes[i]] = node
        return new

    def __getitem__(self, alias):
        return self.cutting(alias)

    def graft(self,
            forest,
            alias = None,
            identified: bool = True,
        ):
        '''
        Glue forest onto another forest at node(s)
        '''
        def grow(offset):
            for lower, upper in forest.sorted(
                    twig = True,
                    level = False,
                    offset = offset,
                    identified = identified):
                self._add_twig(lower, upper)

        if alias is not None: # graft to aliased nodes
            for node in self.aliased(alias):
                offset = self.counter # increase offset with each new node attachment
                for tree in forest.trees:
                    self._add_twig(node, tree.identified(identified, offset))
                grow(offset)
        else: # add as new rooted trees
            offset = self.counter
            for tree in forest.trees:
                self._add_tree(tree.identified(identified, offset))
            grow(offset)

    @unfrozen
    def __setitem__(self, lower, upper):
        if isinstance(upper, Forest):
            self.graft(
                alias = lower,
                forest = upper,
                identified = True)
        else:
            self._add_twig(lower, upper)

    @unfrozen
    def update(self, other):
        '''
        Perform set union when "other" is a Forest;
        otherwise, add a new tree

        Note: MutableMapping mixin
        '''
        if isinstance(other, Forest):
            self.graft(
                alias = None,
                forest = other,
                identified = True)
        else:
            self._add_tree(other)
        return self

    def subtract(self, other):
        '''
        Perform set difference when "other" is a Forest;
        otherwise, delete element

        Note: Encyclopedia mixin
        '''
        new = self.copy()
        if isinstance(other, Forest):
            for t1 in self.trees:
                for t2 in other.trees:
                    if self[t1] == other[t2] and t1 in new:
                        del new[t1]
        else:
            del new[other]
        return new

    def unique(self):
        '''
        Eliminate duplicate trees in a forest
        '''
        new = self.copy()
        trees = sorted(list(self.trees))
        remove=set()
        for i1, t1 in enumerate(trees):
            for t2 in trees[i1+1:]:
                if self[t1] == self[t2]:
                    remove.add(t2)
        for tree in remove:
            del new[tree]
        return new

    def compose(self, other):
        '''
        Composition depends on context of "other":

        - Scaled by integers
        - Acted upon by functions
        - Grafted with Forests
        '''
        new = self.copy()
        if isinstance(other, int):
            for dupe in range(other-1):
                new += self.copy()
        elif isinstance(other, types.FunctionType):
            return self.cutting(morph = other)
        elif isinstance(other, Forest):
            for tree in other.trees:
                if tree.alias in self:
                    for node in self.aliased(tree.alias):
                        for branch in other.branches(tree):
                            new[node] = branch
        else:
            assert False
        return new

    @staticmethod
    def node2alias(generator):
        aliases = {node.alias for node in generator}
        if len(aliases) == 0:
            return {}
        elif len(aliases) == 1:
            return aliases.pop()
        else:
            return aliases


class Test_Forest(unittest.TestCase):

    def setUp(self):
        self.f = f = Forest()
        f += 'G01'
        f['G01'] = 'G11'
        f['G01'] = 'G12'
        f['G11'] = 'G21'
        f['G21'] = 'G31'
        f['G21'] = 'G32'
        f['G21'] = 'G33'
        f['G32'] = 'G41'
        f +=  'G02'

    def test_base(self):
        f1 = self.f
        assert len(f1.trees) == 2
        assert f1.height() == 4
        assert len(f1.canopy()) == len(f1) - 4
        assert 'G21' in f1
        f3 = f1['G21']
        assert f3.counter == f1.counter
        assert len(set(f1.root('G21'))) == 1
        assert len(set(f3.root('G21'))) == 1
        assert Forest.node2alias(f3.root('G21')) == 'G21'
        assert Forest.node2alias(f1.root('G21')) == 'G01'
        f3 = f1.cutting('G21', identified=False)
        assert len(set(f3.above('G21'))) == 3
        assert len(set(f3.below('G21'))) == 0
        assert len(set(f1.below('G21'))) == 1
        assert Forest.node2alias(set(f3.leaves())) == {'G41', 'G33', 'G31'}
        assert f3.counter < f1.counter
        assert 'G01' in f1
        assert 'GX1' not in f1
        f2 = f1['G11']
        assert isinstance(f2, Forest)
        assert len(f2.trees) == 1
        assert len(f2) < len(f1)

    def test_arithmetic(self):
        f1 = self.f.copy()
        f2 = f1.copy()
        f2 += f1.copy()
        assert len(f2) == 2*len(f1)
        f3 = f2 - f1
        assert len(f3) == 0
        f3 = f2 + f1
        assert len(f3) == 3*len(f1)
        f4 = f3.unique()
        assert len(f4) == len(f1)
        assert f4 == f1
        f5 = f1 - f2
        assert len(f5) == 0
        f5 = f1 & f2
        assert f5 == f1
        f6 = f1.copy()
        f5 = f6 & f1
        assert f5 == f1
        f6['G21'] = 'GXX'
        assert f1 != f6
        f5 = f6 & f1
        assert Forest.node2alias(f5.values()) == 'G02'
        assert Forest.node2alias(f5.leaves()) == 'G02'
        assert len(f5) == 1

    def test_aliases(self):
        f = self.f
        f['G01'] = 'G0X'
        f['G21'] = 'G0X'
        l1 = len(f)
        f['G0X'] = 'G0Y'
        assert len(f) == l1 + 2
        assert len(f['G0Y']) == 2

    def test_branching(self):
        f1 = self.f
        f2 = f1.copy()
        assert len(f2) == len(f1)
        assert Forest.equals(f1, f2)
        assert f1['G21'] == f2['G21']
        assert f1['G21'] != f1['G01']
        assert f1 == f2
        f2['G02'] =f2['G21']
        assert len(f2) > len(f1)
        assert not Forest.equals(f1, f2)
        assert f1 != f2
        f3 = f1.cutting(offset=100)
        assert f3 == f1

    def test_iteration(self):
        f1 = self.f
        assert len(list(f1)) ==\
            len(f1.sorted()) ==\
            len(f1.sorted(level=False)) ==\
            len(f1)

    def test_composition(self):
        # scaled
        f1 = self.f
        f2 = 4*f1
        assert len(f2) == 4*len(f1)
        # inner string modification
        def add_x(x):
            return x + 'x'
        f2 = add_x * f1 # modify all the elements
        assert f2 != f1
        assert len(f2) == len(f1)
        def rm_x(x):
            return x[:-1]
        f3 = rm_x * f2
        assert f3 == f1 # undo the modifications
        # element removal
        def rm_g4(x):
            return x if 'G4' not in x else None
        f4 = rm_g4 * f1
        assert len(f4) < len(f1)
        assert 'G41' in Forest.node2alias(f1.leaves())
        assert 'G41' not in Forest.node2alias(f4.leaves())
        # Forest composition
        f5 = Forest()
        f5 += 'G21'
        f5['G21'] = 'G34'
        f5['G34'] = 'G44'
        f5['G44'] = 'G51'
        f6 = f1 * f5
        assert len(f6) == len(f1) + len(f5) - 1
        assert f6.height() == f1.height() + 1

    def test_del(self):
        f1 = self.f.copy()
        f2 = f1.copy()
        del f1['G32']
        assert len(f1) < len(self.f)
        del f2['G41']
        assert len(f1) < len(f2) < len(self.f)

    def test_union(self):
        f1 = self.f.copy()
        f2 = f1.copy()
        f2 += 'G03'
        f2['G03'] = 'G13'

    def test_limb(self):
        f1 = self.f.limb('G41')
        assert list(f1) == ['G01','G11','G21','G32','G41']

if __name__ == '__main__':
    unittest.main()