# -*- coding: utf8 -*-
from abc import ABCMeta, abstractmethod


class Job(object):
    __metaclass__ = ABCMeta

    @abstractmethod
    def wait(self):
        """

        :return:
        """

    @classmethod
    def wait_all(cls, *futures):
        results = []
        for future in futures:
            results.append(future.wait())

        return results
