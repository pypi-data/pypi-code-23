#encoding: UTF-8

from objects_query import QuerySet, Q, FilterObjects


class nFilterObjects(FilterObjects):
    """
    Change default logic form AND to OR
    """
    conditional = False

    def _cmp(self, v1, v2):
        return v1 or v2


class nQ(Q):
    filter_class = nFilterObjects


class NodeQuerySet(QuerySet):
    default_q = nQ

    def __init__(self, iterator, *args, **kwargs):
        super().__init__(iterator, *args, **kwargs)

    @property
    def edges(self):
        """
        :return: QuerySet of Edges for result array of Nodes
        """

        def chain(*args):
            for a in args:
                for i in a:
                    yield i

#        __edges = getattr(self, '_edges', None)
#        if __edges is None:
        self.fetch_all()
        if self.cache:
            # sorting by type
            d = dict()
            for n in self.cache:
                if not n.type in d:
                    d[n.type] = list()
                d[n.type].append(n)
            # union all edges узлов с одинаковыми типами
            es = []
            for nl in d.values():
                es.append({i for i in chain(*[n.iter_edges() for n in nl])})
            # clean
            # del d
            # смотреть итоговое пересечение
            __edges_set = es.pop()
            while len(es) and len(__edges_set):
                __edges_set.intersection_update(es.pop())
        else:
            __edges_set = set()
        __edges = QuerySet(iter(__edges_set))
#            self._edges = __edges
        return __edges
