#encoding: UTF-8

"""
Идея данной БД:
Она основывается на гиперграфе bhg.graph.
Данные, которые индексируются и неизменны вовремени - это вершины графа.
Название "столбцов" - это типы узлов.
Изменяемые данные - это рёбра. 
Таблицы - это типы ребер.

Примерно такая концепция.
Всё работает практически динамически. Сначала задаются только индексы.

Записи представляют собой одномерный словарь значений.

"""

try:
    from .graph import Graph, Edge, Node, DEFAULT_NODE_TYPE
    from .queryset import NodeQuerySet
except:
    from graph import Graph, Edge, Node, DEFAULT_NODE_TYPE
    from queryset import NodeQuerySet


################## utility #################################
class PersistentWrapper():

    def __init__(self, data):
        self.data = data

    def __call__(self, *args, **kwargs):
        return self.data


class toDictIterator():

    def __init__(self, iterator):
        self.iterator = iterator

    def __iter__(self):
        for o in self.iterator:
            yield o.dump_dict()

    def objects(self):
        for o in self.iterator:
            yield o
#############################################################

class GraphDBNode(Node):
    
    def __init__(self, graph, _id = None, type = DEFAULT_NODE_TYPE, *args, **kwargs):
        super().__init__(graph, _id, type, *args, **kwargs)
        setattr(self, str(type), _id)

class GraphDBEdge(Edge):
    """
    Class provide time marks:
    t1 - begin of event
    t2 - end of event
    other fields this
    uniqe meta for event and stored in Nodes
    """
    
    @property
    def t1(self):
        return getattr(self, '_t1', None)
    
    @t1.setter
    def t1(self, value):
        if not hasattr(self, '_t1'):
            self._t1 = value
            self.t2 = value
        elif self._t1 > value:
            self._t1 = value
        elif self.t2 < value:
                self.t2 = value
        else:
            self.t2 = value
    
    def dump_dict(self):
        res = super().dump_dict()
        ns = res['nodes']
        del res['nodes']
        for n in ns:
            if len(ns[n]) > 1:
                res[n] = [o['id'] for o in ns[n]]
            else:
                res[n] = ns[n][0]['id']
        if hasattr(self, '_t1'):
            res['t1'] = self.t1
        return res
    
class GraphDB():
    """
    TODO: pickling or backend storage
    """
    
    class_edge = GraphDBEdge
    class_node = GraphDBNode
    
    def __init__(self, indexes = []):
        self.graph = Graph(class_edge = self.class_edge, class_node = self.class_node)
        self.graph.add_node_types(*indexes)
        self.nodes = NodeQuerySet(self.graph.iter_nodes())
        
    def _get_edges(self, table, data):
        n_ids, d = self.graph.separate_keys(data)
        n = self.graph.nodes(**n_ids)
        e = self.graph.edges(*n, type = table)
        return e, d
    
    def get_native_rows(self, table, data):
        e, d = self._get_edges(table, data)
        del d
        return toDictIterator(e)
    
    def update(self, table, data):
        n_ids, d = self.graph.separate_keys(data)
        n = list(self.graph.nodes(**n_ids))
        e = self.graph.edges(*n, type = table)
        for _e in e:
            _e.update(**d)
        return e
    
    def insert(self, table, data):
        n_ids, d = self.graph.separate_keys(data)
        n = list(self.graph.nodes(**n_ids))
        eid = d.pop('id', None)
        return {self.graph.class_edge(self.graph, eid, type = table, nodes = n, **d)}
    
    def update_or_insert(self, table, data):
        e = self.update(table, data) 
        if not e:
            e = self.insert(table, data)
        return e
    
    def delete(self, table, **kwargs):
        raise NotImplementedError()

        
if __name__ == "__main__":
    

    indexes = ['wiki', 'nic', 'mac']
    data = [
        {'wiki': '101', 'nic': '101--1/0/1', 't1':0, 'mac':'00-11-22', 'source': 'mac'},
        {'wiki': '102', 'nic': '102--1/0/2', 't1':0, 'mac':'00-11-22', 'source': 'mac'},
        {'wiki': '103', 'nic': '103--1/0/1', 't1':0, 'mac':'02-11-22', 'source': 'mac'},
        {'wiki': '101', 'nic': '101--1/0/1', 't1':100, 'mac':'00-11-22', 'source': 'mac'},
        {'wiki': '101', 'nic': '101--1/0/1', 't1':120, 'mac':'00-11-22', 'source': 'mac'},
    ]

    db = GraphDB(indexes)
    
    for d in data:
        table = d.pop('source', 'unk')
        db.update_or_insert(table, d)

    query = db.nodes.filter(nic__endswith = '1/0/1', mac = '00-11-22')
    
    for i in toDictIterator(query.edges):
        print(i)
    for i in toDictIterator(query.edges):
        print(i)

    pass
    