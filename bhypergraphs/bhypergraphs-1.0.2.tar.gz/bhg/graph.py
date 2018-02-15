#encoding: UTF-8

DEFAULT_CHILD_TYPE = 1
DEFAULT_NODE_TYPE = 1
DEFAULT_EDGE_TYPE = 1

class DictL2Iterator():
    """
    Итератор работает с двухуровневым словарем. На втором уровне могут быть как
    словарь так и другое итерируемое
    """

    def __init__(self, data):
        self.data = data

    def __iter__(self):
        for l1 in self.data.values():
            if isinstance(l1, (dict)):
                i = l1.values()
            else:
                i = iter(l1)
            for l2 in i:
                yield l2

class DumpedDictMixin():
    """
    Mixin реализует специальную выборку по аттрибутом класса, 
    которые не начинаются с символа "_"
    """
    
    __not_dumped = []
    
    def __fill_not_dumped(self):
        if not self.__not_dumped:
            self.__class__.__not_dumped = [k for k in self.__dict__.keys() if k[0] == '_' ]

    def dump_dict(self):
        """
        Возвращает dict с аттрибутами класса и их значениями
        """
        self.__fill_not_dumped()
        res = self.__dict__.copy()
        for nd in self.__not_dumped:
            del res[nd]
        return res

class GraphChild(DumpedDictMixin):
    """
    Base class of Node and Edge.
    Functionality: cross-linked
    """

    def __init__(self, graph, func_register_name, func_unregister_name, link_name, _id=None, type=DEFAULT_CHILD_TYPE, *args, **kwargs):
        super().__init__()
        self._graph = graph
        self.id = _id if _id else id(self)
        self.type = type
        f = getattr(graph, func_register_name)
        f(self)
        self._func_unregister = getattr(graph, func_unregister_name)
        self._links = dict()  # dict of sets
        __childs = list(kwargs.pop(link_name, []))
        self.linkto(*__childs)
        self.update(**kwargs)

    def __getstate__(self):
        return self.dump_dict()

    def __setstate__(self, state):
        self.update(**state)

    def update(self, **kwargs):
        for p in kwargs:
            setattr(self, p, kwargs[p])

    def __contains__(self, item):
        return not getattr(self, item, None) is None

    def unregister_self(self):
        for oi in self._links:
            for o in self._links[oi]:
                o._unlink(self)
        self._func_unregister(self)

    def _linkto(self, child):
        type = child.type
        if not type in self._links:
            self._links[type] = set()
        self._links[type].add(child)

    def _unlink(self, child):
        type = child.type
        if type in self._links:
            self._links[type].remove(child)

    def linkto(self, *args):
        for child in args:
            self._linkto(child)
            child._linkto(self)

    def childs(self, type=None):
        if type is None:
            return self.iter_childs()
        elif type in self._links:
            return iter(self._links[type])
        return set()

    def iter_childs(self):
        return DictL2Iterator(self._links)

class Node(GraphChild):
    """
    Класс узла графа. Может наследоваться
    Node(graph, _id = None, type = DEFAULT_NODE_TYPE)
    _id, если не задано, то автоматически генерируется функцией id()
    type - любое значение типов str или int
    """
    def __init__(self, graph, _id=None, type=DEFAULT_NODE_TYPE, *args, **kwargs):
        super().__init__(graph, 'register_node', 'unregister_node', 'edges', _id, type, *args, **kwargs)

    def edges(self, type=None):
        """
        Возвращает итератор множества ребер типа type или всех, если type не указан
        """
        return self.childs(type)

    def iter_edges(self):
        """
        Итератор по ВСЕМ ребрам узла
        """
        return self.iter_childs()


class Edge(GraphChild):
    """
    Класс ребра графа. Может наследоваться
    Edge(graph, _id = None, type = DEFAULT_EDGE_TYPE)
    _id, если не задано, то автоматически генерируется функцией id()
    type - любое значение типов str или int
    """

    def __init__(self, graph, _id = None, type = DEFAULT_EDGE_TYPE, *args, **kwargs):
        super().__init__(graph, 'register_edge', 'unregister_edge', 'nodes', _id, type, *args, **kwargs)

    def nodes(self, type = None):
        """
        Возвращает итератор узлов графа типа type или всех узлов, если type = None
        """
        return self.childs(type)
    
    def iter_nodes(self):
        """
        Итератор по ВСЕМ узлам ребра
        """
        return self.iter_childs()

    def dump_dict(self):
        """
        Возвращает dict с аттрибутами класса и их значениями. 
        Наследован из DumpedDictMixin
        """
        res  = super().dump_dict()
        res['nodes'] = dict([(t, [n.dump_dict() for n in self._links[t]]) for t in self._links])
        return res

    def __getstate__(self):
        d = super().__getstate__()
        d['nodes'] = [(n.type, n.id) for n in self.nodes()]
        return d

class Graph(DumpedDictMixin):
    """
    Класс гиперграфа
    Graph(class_node = Node, class_edge = Edge)

    TODO: pickling
    """
    
    def __init__(self, class_node = Node, class_edge = Edge):
        super().__init__()
        self._nodes = dict()
        self._edges = dict()
        self.class_node = class_node
        self.class_edge = class_edge
        
    def register_node(self, node):
        """
        вн. функция, специально не использовать
        """
        if not node.type in self._nodes:
            self._nodes[node.type] = dict()
        self._nodes[node.type][node.id] = node

    def unregister_node(self, node):
        """
        вн. функция, специально не использовать
        """
        del self._nodes[node.type][node.id]

    def register_edge(self, edge):
        """
        вн. функция, специально не использовать
        """
        if not edge.type in self._edges:
            self._edges[edge.type] = list()
        self._edges[edge.type].append(edge)

    def unregister_edge(self, edge):
        """
        вн. функция, специально не использовать
        """
        self._edges[edge.type].remove(edge)
        
    def node(self, _id = None, type = DEFAULT_NODE_TYPE, *args, **kwargs):
        """
        Возвращает узел графа с указанными _id и type,
        Если такого не найдено, то создаёт новый с указанными _id и type и 
        передавая без изменений в конструктор дополнительные args и kwargs
        """
        if type in self._nodes:
            if _id in self._nodes[type]:
                return self._nodes[type][_id]
        return self.class_node(self, _id, type = type, *args, **kwargs)
    
    def add_node_types(self, *args):
        """
        TODO docs
        """
        for nt in args:
            if not nt in self._nodes:
                self._nodes[nt] = dict()
                
    def nodes(self, **kwargs):
        """
        Возвращает все узлы графа которые запрашиваются в параметрах
        nodes(node_type=node_id, ...)
        """
        for nt in kwargs:
            if nt in self._nodes:
                yield self.node(kwargs[nt], type = nt)
    
    def separate_keys(self, d):
        """
        Разделяет dict d на два словаря. В первый относятся все те у которых key 
        это тип узла. Во второй всё остальное. Возвращает tuple из двух dict
        """
        nk = dict()
        at = dict()
        for k in d:
            if k in self._nodes:
                nk[k] = d[k]
            else:
                at[k] = d[k]
        return nk, at
    
    def edges(self, *args, **kwargs):
        """
        Возвращает множество set() ребер графа, которые имеют тип type
        и являются общими для всех указанных узлов графа.
        
        edges([node1[,node2...]],[type=None])
        """
        type = kwargs.get('type', None)
        nodes = list(args)
        if not len(nodes):
            return set()
        node = nodes.pop()
        rs = set()
        rs.update(node.edges(type))
        while nodes and len(rs):
            rs.intersection_update(nodes.pop().edges(type))
        return rs

    def iter_edges(self):
        """
        Итератор по ВСЕМ ребрам графа
        """
        return DictL2Iterator(self._edges)
    
    def iter_nodes(self):
        """
        Итератор по ВСЕМ узлам графа
        """
        return DictL2Iterator(self._nodes)

    @property
    def count_nodes(self):
        """
        Количество узлов в графе
        """
        c = 0
        for v in self._nodes.values():
            c += len(v)
        return c
    
    @property
    def count_edges(self):
        """
        Количество ребер в графе
        """
        c = 0
        for v in self._edges.values():
            c += len(v)
        return c
    
    def node_types(self):
        return self._nodes.keys()
    
    def edge_types(self):
        return self._edges.keys()

    def __getstate__(self):
        d = self.dump_dict()
        d['nodes'] = [n.__getstate__() for n in self.iter_nodes()]
        d['edges'] = [e.__getstate__() for e in self.iter_edges()]
        return d

    def __setstate__(self, state):
        ss_nodes = state.pop('nodes')
        ss_edges = state.pop('edges')
        self.__dict__.update(state)
        self.__init__(self.class_node, self.class_edge)
        #create nodes
        for n in ss_nodes:
            nt = n.pop('type')
            nid = n.pop('id')
            self.node(nid, nt, **n)
        #create edges
        for e in ss_edges:
            et = e.pop('type')
            eid = e.pop('id')
            en = e.pop('nodes')
            nd = dict(en)
            n = list(self.nodes(**nd))
            self.class_edge(self, eid, et, nodes = n, **e)

if __name__ == "__main__":
    
    import time
    
    g = Graph()
    
    st = time.time()
    
    node_types = ['wiki', 'nic', 'mac']
    data = [
        {'wiki': '101', 'nic': '101--1/0/1', 't1':0, 't2': 1, 'mac':'00-11-22', 'source': 'mac'},
        {'wiki': '102', 'nic': '102--1/0/1', 't1':0, 't2': 2, 'mac':'01-11-22', 'source': 'mac'},
        {'wiki': '103', 'nic': '103--1/0/1', 't1':0, 't2': 3, 'mac':'02-11-22', 'source': 'mac'},
        {'wiki': '101', 'nic': '101--1/0/1', 't1':100, 't2': 1, 'mac':'00-11-22', 'source': 'mac'},
    ]
    
    g.add_node_types(*node_types)

    for ed in data:
        n_ids, p = g.separate_keys(ed)
        et = p.pop('source')
        n = list(g.nodes(**n_ids))
        _e = set(g.edges(*n, type = et))
        if not _e:
            _e = {Edge(g, type = et, nodes = n, **p)}
        else:
            for __e in _e:
                __e.update(**p)
    
    print(time.time() - st ,'s')

    for _e in g._edges:
        for __e in g._edges[_e]:
            print(__e.dump_dict())

    print(g.__getstate__())

    import pickle

    dump = pickle.dumps(g)

    print('-' * 60)

    ng = pickle.loads(dump)

    print(ng.__getstate__())
    
    for _e in ng._edges:
        for __e in ng._edges[_e]:
            print(__e.dump_dict())


