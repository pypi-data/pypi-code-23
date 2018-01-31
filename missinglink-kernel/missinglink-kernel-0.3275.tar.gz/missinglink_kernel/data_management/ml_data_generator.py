# -*- coding: utf8 -*-


class MLDataGenerator(object):
    def __init__(self, volume_id, query, data_callback, cache_directory, batch_size=32, use_threads=False, processes=-1):
        self.__cache_directory = cache_directory
        self.__volume_id = volume_id
        self.__query = query
        self.__data_callback = data_callback
        self.__batch_size = batch_size
        self.__use_threads = use_threads
        self.__processes = processes

    def flow(self):
        from .legit.scam import QueryParser, visit_query, resolve_tree
        from .legit.multi_process_control import get_multi_process_control
        from .query_data_generator import QueryDataGenerator
        from .query_visitors import SplitVisitor, RemoveSplitTransformer

        tree = QueryParser().parse_query(self.__query)

        split_visitor = SplitVisitor()
        visit_query(split_visitor, tree)

        multi_process_control = get_multi_process_control(self.__processes, use_threads=self.__use_threads)

        for phase in ['train', 'test', 'validation']:
            if split_visitor.split.get(phase) is None:
                continue

            resolved_tree = resolve_tree(tree)
            resolved_tree = RemoveSplitTransformer(phase)(resolved_tree)

            query = str(resolved_tree)
            yield QueryDataGenerator(
                multi_process_control,
                self.__cache_directory, self.__data_callback, self.__volume_id, query, self.__batch_size)
