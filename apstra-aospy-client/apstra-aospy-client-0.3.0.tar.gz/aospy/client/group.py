# Copyright 2014-present, Apstra, Inc. All rights reserved.
#
# This source code is licensed under End User License Agreement found in the
# LICENSE file at http://www.apstra.com/community/eula

import six
import json
from bidict import namedbidict

from .groupitem import GroupItem, GroupDictItem
from .utils import itemgetter


__all__ = ['Group', 'GroupItem',
           'GroupDict', 'GroupDictItem']


# #############################################################################
# #############################################################################
#
#                                 Group
#
# #############################################################################
# #############################################################################


GroupIndex = namedbidict('GroupIndex', 'id', 'label')


class Group(object):
    # :data:`group_endpoint` class value is the API endpoint,
    # not including the prefix "/api".
    group_endpoint = None

    # :data:`groupitem_label` class value identifies the API property associated
    # with the user-defined name.  Not all items use the same API property.

    groupitem_label = 'label'

    #: :data:`UID` class value identifies the API property associated with the AOS unique ID.  Not
    #: all items use the same API property.

    groupitem_id = 'id'

    #: :data:`GROUP_ITEMS` class value identies the item in the REST body when
    #: the GET operation is involved to return all of the items in the group

    group_items = 'items'

    #: Item identifies the class used for each instance within this collection.  All derived classes
    #: will use the :class:`GroupItem` as a base class.

    groupitem_class = GroupItem

    class ItemIter(object):
        def __init__(self, group):
            self.group = group

            # using keys() to make a copy of the key list to avoid the issue
            # of revmoving items from a dictionary while iterating over it.
            self.iter = iter(list(self.group.index.id_for.keys()))

        def next(self):
            return self.group[six.next(self.iter)]

        __next__ = next

    def __init__(self, context, *vargs, **kwargs):
        self.context = context
        self.api = context.api

        self.url = "%s%s" % (context.url, self.__class__.group_endpoint)
        if not hasattr(self, 'get_item_id'):
            self.get_item_id = itemgetter(self.__class__.groupitem_id)

        if not hasattr(self, 'get_item_label'):
            self.get_item_label = itemgetter(self.__class__.groupitem_label)

        self.last_fetched_catalog_body = dict()

        # index stores a bidict of <id> / <label> values
        self.index = GroupIndex()

        # catalog stores a collection of group item instances, index by <id>
        self._catalog = dict()

    # =========================================================================
    #
    #                             PROPERTIES
    #
    # =========================================================================

    @property
    def labels(self):
        """
        Returns a list of <label> values for items in the group.  If
        the existing index is empty, then accessing this attribute will
        cause the group to :meth:`refresh` the group contents.
        """
        if not len(self.index.id_for):
            self.reload()

        return list(self.index.id_for.keys())

    @property
    def ids(self):
        """
        Returns a list of <id> values for items in the group.  If
        the existing index is empty, then accessing this attribute will
        cause the group to :meth:`refresh` the group contents.
        """
        if not len(self.index):
            self.reload()

        return list(self.index.keys())

    @property
    def catalog(self):
        return self._catalog if len(self._catalog) else self.fetch_items()

    # =========================================================================
    #
    #                             PUBLIC METHODS
    #
    # =========================================================================

    def fetch_items_hook(self, catalog_data):
        """
        Used to provide item data for each item in the fetched catalog.
        This hook method exists for subclass group items that do not follow
        the AOS standard GET response of {'items': [{dict}, {dict}, ...]}
        """

        # the catalog items could be either a list or a dict.  choose
        # the iterable based on the type value.

        items = catalog_data[self.group_items]
        item_iter = six.iteritems(items) if isinstance(items, dict) else iter(items)

        # return the items as a generator for consumption
        return (item for item in item_iter)

    def fetch_items(self):
        """
        fetches the latest group data from the server and rebuilds the group
        catalog item instances.  Returns the dictionary of existing instances.
        """
        self._catalog.clear()
        self.index.clear()

        got = self.api.get(self.url)
        if not got.ok:
            raise RuntimeError(
                'unable to fetch catalog, code=%d, reason=%s' %
                (got.status_code, got.reason),
                self, got)

        for itemdata in self.fetch_items_hook(got.json()):
            self.group_add_item(self.groupitem_class(self, itemdata))

        return self._catalog

    def reload(self):
        """ perform the catalog fetch/rebuild, but does not return anything """
        self.fetch_items()

    def purge(self, confirm):
        """ must explicitly pass confirm='YES' for this to execute """
        assert confirm == 'YES'
        for item in self:
            item.delete()

    # -------------------------------------------------------------------------
    # group methods
    # -------------------------------------------------------------------------

    def group_add_item(self, item):
        """ add an item instance to the group """
        item_name = self.get_item_label(item.obj)
        item_id = self.get_item_id(item.obj)

        assert item_id and item_name

        self.index[item_id] = item_name
        self._catalog[item_id] = item

    def group_remove_item(self, item):
        """ remove an item from the group.  does not delete the item instance """
        item_id = item.id
        assert item_id

        del self.index[item_id]
        del self._catalog[item_id]

    # -------------------------------------------------------------------------
    # item methods
    # -------------------------------------------------------------------------

    def item_new(self, item_label=None, item_data=None):
        """
        Return a new group item instance.

        Parameters
        ----------
        item_label : str
            optional, new item label value.

        item_data : dict
            optional, new item value

        Raises
        ------
        AssertionError if `item_label` provided, and already exists in
        the group

        Returns
        -------
        object
            group item instance, created from the `groupitem_class`.
        """
        if not len(self.index):
            self.reload()

        # we don't want to allow duplicate names.  This is not a
        # specific restriction of the REST API.
        assert item_label not in self.index.id_for

        # return a new group item instance
        return self.groupitem_class(self, item_data or {}, label=item_label)

    def item_for_id(self, item_id):
        """
        return an existing group item based on the item id value.  Raise
        ValueError if this item does not exist.
        """
        if not len(self.index):
            self.reload()

        if item_id not in self._catalog:
            raise ValueError(
                'item id=%s does not exist in catalog' % item_id)

        return self._catalog[item_id]

    def item_for_label(self, item_label):
        """
        Return an existing group item based on the item label value.
        Raise ValueError if thie item does not exist.
        """
        if not len(self.index):
            self.reload()

        if item_label not in self.index.id_for:
            raise ValueError(
                'item label=%s does not exist in catalog' % item_label)

        return self._catalog[self.index.id_for[item_label]]

    def item_import(self, item_data):
        item = self.item_new(item_label=self.get_item_label(item_data),
                             item_data=item_data)

        item.create(replace=True)
        return item

    # =========================================================================
    #
    #                             OPERATORS
    #
    # =========================================================================

    def __contains__(self, label):
        """ checks if a given label exists in the index """
        if not len(self.index):
            self.fetch_items()

        return label in self.index.id_for

    def __getitem__(self, label):
        """ get an item by label value """

        if not len(self.index):
            self.fetch_items()

        item_id = self.index.id_for.get(label)
        return (self._catalog[item_id] if item_id
                else self.groupitem_class(self, {}, label=label))

    def __iter__(self):
        if not len(self._catalog):
            self.fetch_items()

        return self.ItemIter(self)

    def __iadd__(self, other):
        if not isinstance(other, GroupItem):
            raise ValueError(
                "attempting to add invalid item type '%s'" %
                str(type(other)))

        self.group_add_item(other)
        return self

    def __isub__(self, other):
        if not isinstance(other, GroupItem):
            raise ValueError(
                "attempting to remove invalid item type '%s'" %
                str(type(other)))

        self.group_remove_item(other)
        return self

    def __str__(self):
        cls = self.__class__
        return json.dumps({
            'uri': cls.group_endpoint,
            'by_label': cls.groupitem_label,
            'by_id': cls.groupitem_id,
            'labels': self.labels
        }, indent=3)

    __repr__ = __str__


class GroupDict(Group):
    groupitem_class = GroupDictItem

    @classmethod
    def get_item_id(cls, obj):
        return obj[0]

    @classmethod
    def get_item_label(cls, obj):
        try:
            return obj[1][cls.groupitem_label]
        except KeyError:
            return None
