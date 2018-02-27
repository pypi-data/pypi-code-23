
class GraphValue:
    def __init__(self, value, is_ref=False):
        self.value = value
        self.is_ref = is_ref

    def __hash__(self):
        return hash((self.value, self.is_ref))

    def __eq__(self, other):
        return (self.value, self.is_ref) == (other.value, other.is_ref)

    def __str__(self):
        return str(self.value) if not self.is_ref else '<' + str(self.value) + '>'

class Graph:
    def __init__(self):
        self._spo = {}
        self._pos = {}
        self._osp = {}
        self.count = 0

    def __len__(self):
        return self.count

    def merge(self, graph):
        for s, p, o in graph.triples():
            self.add(s, p, o)

    def add(self, s, p, o):
        Graph.__add_to_index(self._spo, s, p, o)
        Graph.__add_to_index(self._pos, p, o, s)
        if Graph.__add_to_index(self._osp, o, s, p):
            self.count += 1

    def remove(self, s, p, o):
        pass

    @staticmethod
    def __add_to_index(index, x, y, z):
        if x not in index:
            index[x] = {y:{z}}
            return True            
        if y not in index[x]:
            index[x][y] = {z}
            return True
        s = index[x][y]
        before = len(s)
        s.add(z)
        after = len(s)
        return after > before

    def triples(self):
        for s in self._spo:
            for p in self._spo[s]:
                for o in self._spo[s][p]:
                    yield s, p, o

    def get_by_subject(self, s):
        for p in self._spo[s]:
            for o in self._spo[s][p]:
                yield s, p, o
        
    def get_by_subject_predicate(self, s, p):
        for o in self._spo[s][p]:
            yield s, p, o

    def get_by_predicate(self, p):
        for o in self._pos[p]:
            for s in self._pos[p][o]:
                yield s, p, o

    def get_by_predicate_object(self, s, p):
        for o in self._pos[p][o]:
            yield s, p, o

    def get_by_object(self, o):
        for s in self._osp[o]:
            for p in self._osp[o][s]:
                yield s, p, o

    def get_by_object_subject(self, o, s):
        for p in self._osp[o][s]:
            yield s, p, o

    def contains(self, s, p, o):
        if s in self._spo:
            tpo = self._spo[s]
            if p in tpo:
                to = tpo[p]
                return o in to
        return False

    def contains_graph(self, g):
        for s, p, o in g.triples():
            if not self.contains(s, p, o):
                return False
        return True

    def equals(self, g):
        if len(self) != len(g):
            return False
        return self.contains_graph(g)
   

def print_triple(t):
    print('<' + str(t[0]) + '> <' + str(t[1]) + '> ' + str(t[2]))

def print_graph(graph):
    for t in graph.triples():
        print_triple(t)
