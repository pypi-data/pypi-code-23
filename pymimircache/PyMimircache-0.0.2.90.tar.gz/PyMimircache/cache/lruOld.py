# coding=utf-8
from PyMimircache.cache.abstractCache import Cache
from PyMimircache.utils.linkedList import LinkedList


class LRU(Cache):
    def __init__(self, cache_size=1000, **kwargs):

        super().__init__(cache_size, **kwargs)
        self.cacheLinkedList = LinkedList()
        self.cacheDict = dict()  # key -> linked list node (in reality, it should also contains value)

    def __len__(self):
        return len(self.cacheDict)

    def has(self, req_id, **kwargs):
        """
        :param **kwargs:
        :param req_id:
        :return: whether the given element is in the cache
        """
        if req_id in self.cacheDict:
            return True
        else:
            return False

    def _update(self, req_item, **kwargs):
        """ the given element is in the cache, now update it to new location
        :param **kwargs:
        :param req_item:
        :return: None
        """

        node = self.cacheDict[req_item]
        self.cacheLinkedList.move_node_to_tail(node)

    def _insert(self, req_item, **kwargs):
        """
        the given element is not in the cache, now insert it into cache
        :param **kwargs:
        :param req_item:
        :return: evicted element or None
        """
        return_content = None
        node = self.cacheLinkedList.insert_at_tail(req_item)
        self.cacheDict[req_item] = node
        return return_content

    def _printCacheLine(self):
        for i in self.cacheLinkedList:
            try:
                print(i.content, end='\t')
            except:
                print(i.content)

        print(' ')

    def evict(self, **kwargs):
        """
        evict one element from the cache
        :param **kwargs:
        :return: content of evicted element
        """

        content = self.cacheLinkedList.remove_from_head()
        del self.cacheDict[content]
        return content

    def access(self, req_item, **kwargs):
        """
        :param **kwargs: 
        :param req_item: the element in the trace, it can be in the cache, or not
        :return: None
        """
        if self.has(req_item, ):
            self._update(req_item, )
            return True
        else:
            self._insert(req_item, )
            if self.cacheLinkedList.size > self.cache_size:
                self.evict()
            return False

    def __repr__(self):
        return "LRU cache of size: {}, current size: {}, {}".\
            format(self.cache_size, self.cacheLinkedList.size, super().__repr__())
