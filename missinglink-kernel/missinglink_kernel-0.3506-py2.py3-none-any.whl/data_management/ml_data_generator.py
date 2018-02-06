# -*- coding: utf8 -*-
class MLDataGenerator(object):
    def __init__(self, volume_id, query, data_callback, cache_directory, batch_size=32, use_threads=False, processes=-1):
        self.__volume_id = volume_id
        self.__query = query
        self.__data_callback = data_callback
        self.__batch_size = batch_size
        self.__use_threads = use_threads
        self.__processes = processes
        self.__storage = self.__create_cache_storage(cache_directory)

    @classmethod
    def __create_cache_storage(cls, cache_directory):
        from .cache_storage import CacheStorage

        return CacheStorage(cache_directory)

    def flow(self):
        from .legit.scam import QueryParser, visit_query, resolve_tree
        from .legit.multi_process_control import get_multi_process_control
        from .query_data_generator import QueryDataGeneratorFactory
        from .query_visitors import SplitVisitor, RemoveSplitTransformer, GroupVisitor

        tree = QueryParser().parse_query(self.__query)

        split_visitor = visit_query(SplitVisitor(), tree)

        multi_process_control = get_multi_process_control(self.__processes, use_threads=self.__use_threads)

        factory = QueryDataGeneratorFactory(
            multi_process_control, self.__storage, self.__data_callback,
            self.__volume_id, self.__batch_size)

        for phase in ['train', 'test', 'validation']:
            if not split_visitor.has_phase(phase):
                continue

            resolved_tree = resolve_tree(tree, RemoveSplitTransformer(phase))

            query = str(resolved_tree)

            yield factory.create(query)
