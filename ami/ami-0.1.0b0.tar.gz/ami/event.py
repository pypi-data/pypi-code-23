# -*- coding: utf-8 -*-

from uuid import uuid4
from collections import defaultdict, namedtuple


def _is_sub_dict(subset, superset):
    for key, value in subset.items():
        if key in superset.keys():
            if value not in superset[key]:
                return False
        else:
            return False
    return True


class AmiPublisherSubscriber(object):
    """
    Example::
        >>> self.when({}, {})(lambda event: ...)
    
        >>> self.when({}, {}, ..., {})
        >>> def handler(event):
        >>>     ...

    """

    _pointers = None
    _PsSubscriptionPoint = namedtuple('_PsSubscriptionPoint', 'uid cuid predicat handler')

    def __init__(self):
        self._pointers = defaultdict(list)

    def when(self, *patterns):
        def decarator(handler, uid=None, cuid=None):
            return self._when(patterns, handler, uid, cuid)
        return decarator

    @property
    def size(self):
        return sum(len(values) for values in self._pointers.values())

    def _when(self, patterns, handler, uid, cuid):
        """
        :param: uid - id for handler
        :param: cuid - id for handler class
        """

        subscription = self._PsSubscriptionPoint(
            uid or uuid4(),
            cuid,
            predicat=self._make_predicat(patterns),
            handler=handler
        )

        self._pointers[cuid].append(subscription)

        return subscription

    def fire(self, event_instance):
        for subscription_pointers in self._pointers.values():
            for subscription_pointer in subscription_pointers:
                if subscription_pointer.predicat(event_instance):
                    subscription_pointer.handler(event_instance)
        return self

    def _make_predicat(self, patterns):

        def predicat(event_instance):
            if not isinstance(event_instance, dict):
                return False

            return any(_is_sub_dict(pattern, event_instance) for pattern in patterns)

        return predicat
