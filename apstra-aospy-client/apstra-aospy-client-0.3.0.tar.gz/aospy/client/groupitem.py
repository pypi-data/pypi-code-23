# Copyright 2014-present, Apstra, Inc. All rights reserved.
#
# This source code is licensed under End User License Agreement found in the
# LICENSE file at http://www.apstra.com/community/eula

from copy import copy
import json

import retrying


# #############################################################################
# #############################################################################
#
#                                Group Item
#
# #############################################################################
# #############################################################################

class GroupItem(object):
    """
    An item within a given :class:`Collection`.  The following public attributes
    are available:

        * :attr:`name` - the user provided item name
        * :attr:`api` - the instance to the :mod:`Session.Api` instance.

    """
    def __init__(self, *vargs, **kwargs):
        self.group, self.obj = vargs
        self.api = self.group.api
        self._init_label = kwargs.get('label')

    # =========================================================================
    #
    #                             PROPERTIES
    #
    # =========================================================================

    @property
    def label(self):
        return self.group.get_item_label(self.obj) or self._init_label

    # -------------------------------------------------------------------------
    # PROPERTY: id
    # -------------------------------------------------------------------------

    @property
    def id(self):
        try:
            return self.group.get_item_id(self.obj)
        except KeyError:
            return None

    @id.setter
    def id(self, new_value):
        self.value[self.group.groupitem_id] = new_value

    # -------------------------------------------------------------------------
    # PROPERTY: url
    # -------------------------------------------------------------------------

    @property
    def url(self):
        if not self.exists:
            raise RuntimeError(
                'item label=%s has no id value' % self.label,
                self, self.group.url)

        return "%s/%s" % (self.group.url, self.id)

    # -------------------------------------------------------------------------
    # PROPERTY: exists
    # -------------------------------------------------------------------------

    @property
    def exists(self):
        return bool(self.id)

    # -------------------------------------------------------------------------
    # PROPERTY: value
    # -------------------------------------------------------------------------

    @property
    def value(self):
        return self.obj

    @value.setter
    def value(self, new_value):
        self.obj = copy(new_value)

    @value.deleter
    def value(self):
        self.delete()

    # =========================================================================
    #
    #                             PUBLIC METHODS
    #
    # =========================================================================

    def write(self, value=None, command='put'):
        if not self.exists:
            return self.create(value=value)

        cmd = getattr(self.api, command)
        got = cmd(self.url, json=value or self.value)

        if not got.ok:
            raise RuntimeError(
                'unable to update: %s' % got.reason,
                self, got)

        self.read()

    def get(self):
        got = self.api.get(self.url)
        if not got.ok:
            raise RuntimeError(
                'unable to get item (id=%s, label=%s): %s' %
                (self.id, self.label, got.reason),
                self, got)

        return got

    def read(self):
        """
        Retrieves the item value from the AOS-server.

        Raises:
            SessionRqstError: upon REST call error

        Returns: a copy of the item value, usually a :class:`dict`.
        """

        got = self.get()
        self.obj = copy(got.json())
        return self.obj

    def create(self, value=None, replace=False, timeout=5000):
        # check to see if this item currently exists, using the name/URI
        # when this instances was instantiated from the collection; *not*
        # from the `value` data.

        def throw_duplicate(name):
            raise ValueError(
                "'%s' already exists in group: %s" %
                (name, self.group.group_endpoint), self)

        if self.exists:
            if not replace:
                throw_duplicate(self.label)

            try:
                self.delete()
            except RuntimeError as exc:
                resp = exc.args[2]
                if resp.status_code != 404:
                    raise

        # the caller can either pass the new data to this method, or they
        # could have already assigned it into the :prop:`value`.  This
        # latter approach should be discouraged.

        if value is not None:
            self.value = value

        # now check to see if the new value/name exists.  if the value
        # does not include the label value, we need to auto-set it from
        # the instance name value.

        new_name = self.group.get_item_label(self.value)
        if not new_name:
            new_name = self.label
            self.value[self.group.groupitem_label] = new_name

        if new_name in self.group:
            throw_duplicate(new_name)

        # at this point we should be good to execute the POST and
        # create the new item in the server

        got = self.api.post(self.group.url, json=self.value)
        if not got.ok:
            raise RuntimeError('unable to create item', self, got)

        body = got.json()

        @retrying.retry(wait_fixed=1000, stop_max_delay=timeout)
        def await_item():
            self.group.fetch_items()
            assert new_name in self.group.labels

        uid = body.get('id') or self.group.get_item_id(body)
        while not uid:
            await_item()
            body = self.group.catalog[new_name]

        self.id = body.get('id') or self.group.get_item_id(body)

        # now add this item to the parent collection so it can be used by other
        # invocations

        self.group += self
        return self

    def delete(self, retain=False):
        """
        Deletes the item from the AOS server

        Raises:
            SessionRqstError - when API error
            NoExistsError - when item does not actually exist
        """
        got = self.api.delete(self.url)
        if not got.ok:
            raise RuntimeError(
                'unable to delete item: %s' % got.reason,
                self, got)

        if not retain:
            self.group -= self
            self.obj = {}

    def dumps(self, filepath=None, fileobj=None, indent=3):
        fileobj = fileobj or open(filepath or self.label + ".json", 'w+')
        json.dump(self.value, fileobj, indent=indent)

    def loads(self, filepath):
        self.obj = json.load(open(filepath))

    def __getitem__(self, item):
        """ helper to get item out of the value """
        return self.value[item]

    def __str__(self):
        return json.dumps({
            'label': self.label,
            'id': self.id,
            'value': self.value
        }, indent=3)

    __repr__ = __str__


class GroupDictItem(GroupItem):
    def __init__(self, *vargs, **kwargs):
        super(GroupDictItem, self).__init__(*vargs, **kwargs)
        if not self.obj:
            self.obj = [None, {}]

    @property
    def value(self):
        return self.obj[1]

    @value.setter
    def value(self, new_value):
        self.obj[1] = copy(new_value)

    @property
    def id(self):
        return self.obj[0]

    @id.setter
    def id(self, new_value):
        self.obj[0] = new_value
