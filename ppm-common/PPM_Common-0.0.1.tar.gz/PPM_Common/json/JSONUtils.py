# -*- coding: utf-8 -*-
"""
..  py:module:: JSONUtils

This module contain JSONUtils class
.. moduleauthor:: jérôme
"""
import logging
import json

logger = logging.getLogger("JSONUtils")


class JSONUtils(object):
    """
    ..  py:class:: JSONUtils()

    Class that contain utils for json data and/or dict data

    ..  warning:: all methods are statics

    """

    @staticmethod
    def search_value(key, dictData):
        """
        ..  py:function:: search_value(key)

        This method search a value with key parameter. A list can be returned.

        :param key: the researched key
        :type key: basestring
        :param dictData: the dict for search
        :type dictData: dict, list
        :return: a list with one or more element that corresponding to key
        :rtype: list
        :raise: TypeError, ValueError, Exception
        """

        if not isinstance(key, str):
            raise TypeError("Key must be string or Unicode")

        data = dictData
        result = list()

        if not isinstance(dictData, (dict, list)):
            if not isinstance(dictData, str):
                raise TypeError("dictData must be a json string or a dict")

            # try to load it in dict
            try:
                data = json.loads(dictData)
            except Exception as e:
                logger.exception(e)

        if isinstance(data, dict):
            # for key, value in data dict
            for k, v in data.items():
                # if k is the key then return value of k
                if k == key:
                    if isinstance(v, list):
                        result.extend(v)
                    else:
                        result.append(v)
                    return result

                # if not the good key, regarding if value is a sublist of dict
                if isinstance(v, list):
                    # if yes, then iterate the list
                    for d in v:
                        # recall the function recursively
                        if isinstance(d, dict):
                            result.extend(JSONUtils.search_value(key, d))
        elif isinstance(data, list):
            # if yes, then iterate the list
            for d in data:
                # recall the function recursively
                if isinstance(d, dict):
                    result.extend(JSONUtils.search_value(key, d))

        # return result list : empty list if no key was founded
        return result

    @staticmethod
    def search_composite(compositeKey, dictData):
        """
        ..  py:function:: search_composite(compositeKey, dictData)

        Search a key composed with keyword separated by dot : nnn.fff.ppp

        :param compositeKey: the searched key
        :type compositeKey: str
        :param dictData: dict or list that contain data
        :type dictData: dict, list
        :return: result .. None if no key was founded
        :rtype: list
        """

        if not isinstance(compositeKey, str):
            raise TypeError("Key must be string or Unicode")

        data = dictData

        if not isinstance(dictData, (dict, list)):
            if not isinstance(dictData, str):
                raise TypeError("dictData must be a json string or a dict")

            # try to load it in dict
            try:
                data = json.loads(dictData)
            except Exception as e:
                logger.exception(e)

        # composite key are self or self.other or self.other.another
        # search value for first lvl
        keyList = compositeKey.split(".", 1)

        key = keyList[0]

        value = JSONUtils.search_value(key, data)

        if len(keyList) > 1:
            if not keyList[1]:
                return value
            else:
                value = JSONUtils.search_composite(keyList[1], value)

        return value
