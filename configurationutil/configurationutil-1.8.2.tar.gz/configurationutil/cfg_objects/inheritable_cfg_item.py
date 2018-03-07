# encoding: utf-8

from copy import deepcopy
from fdutil.dict_tools import recursive_update
from .cfg_item import CfgItem


class InheritableCfgItem(CfgItem):

    """ A Config item that supports inheritance. """

    # Define how params missing from config file should be handled.
    # If STRICT is True:
    #       Loading the 'defaults' params starts from an empty dict.  Therefore
    #       if the default param has not been defined a KeyError will be raised
    #       when the param is accessed.
    # If STRICT is False:
    #       Loading the 'defaults' params starts from the .  Therefore
    #       if the default param has not been defined the param will be looked up
    #       in the DEFAULT_PARAMS dict only if the param also does not exist in
    #       the DEFAULT_PARAMS dict will a KeyError be raised.
    STRICT = True

    # DEFAULT_PARAMS is used for:
    #    -> 'defaults' default return params as described for STRICT above.
    #    -> The source of truth for allowable 'defaults' params.  Params will
    #       only be allowed to be added to defaults if they exist in DEFAULT_PARAMS
    #       otherwise they will be added to parameters dict.
    DEFAULT_PARAMS = {}

    # Allows for a deeper inheritance.
    # If True: inheritance is done for all nested dicts
    # If False: inheritance is done only for the defaults dict.
    INHERIT_RECURSIVELY = False

    # DO NOT EDIT / OVERRIDE these
    HIDDEN = u'hidden'
    INHERITS = u'inherits'
    DEFAULTS = u'defaults'

    @property
    def hidden(self):
        # If hidden is not set then we default to False as items should always
        # be shown unless explicitly hidden.
        return self.get(self.HIDDEN, False)

    @property
    def _default_inheritable_params(self):

        """ For class internal use only!

        Loads configured default inheritable params depending on self.STRICT.

        :return:    (dict) containing the default inheritable params.
        """

        return {} if self.STRICT else deepcopy(self.DEFAULT_PARAMS)

    @property
    def _base_item_overrides(self):

        """ For class internal use only!

        Loads configured base item params. ('inherit' param)

        :return:    (dict) containing the configured base items params.
        """

        try:
            base_item_name = self.parameters[self.INHERITS]

        except KeyError:
            # No base item set
            return None

        else:
            base_item = self.__class__(cfg_fn=self._cfg_fn,
                                       cfg_root=self._cfg_root,
                                       key=base_item_name,
                                       key_name=self._key_name)

            return base_item.inheritable_parameters

    @property
    def _item_overrides(self):

        """ For class internal use only!

        Loads this items configured params. ('defaults' param)

        :return:    (dict) containing the configured items params.
        """

        try:
            return self.parameters[self.DEFAULTS]

        except KeyError:
            # we are not overriding anything so nothing to do!
            return None

    @property
    def inheritable_parameters(self):

        """ For class internal use only!

        Loads configured inheritable params.  This can then
        be used by __getitem__ etc. to get individual params.

        :return:    (dict)  containing the final set or params after
                            inheritance has been worked out.
        """

        # create defaults dict
        current_params = self._default_inheritable_params

        # Get base item defaults and update defaults dict
        current_params = self._inherit(current_params, self._base_item_overrides)

        # get this item's overrides and update inheritable params dict
        current_params = self._inherit(current_params, self._item_overrides)

        return self._apply_override(current_params)

    def _inherit(self,
                 current,
                 new):

        if new is not None:
            if self.INHERIT_RECURSIVELY:
                current = recursive_update(current, new)

            else:
                current.update(new)

        return current

    def __getitem__(self, item):

        try:
            return self.inheritable_parameters[item]

        except KeyError:
            return super(InheritableCfgItem, self).__getitem__(item)

    def __setitem__(self, item, value):

        if item in self.DEFAULT_PARAMS:
            # The param belongs in defaults
            if self.DEFAULTS in self.parameters:
                self._parameters[self.DEFAULTS][item] = value

            else:
                # Do defaults yet so create it!
                self._parameters[self.DEFAULTS] = {
                    item: value
                }

        elif item == self._key_name:
            self._key_attr = value

        else:
            # The param does not belong in defaults
            self._parameters[item] = value

    def __delitem__(self, item):
        if self.DEFAULTS in self.parameters:
            del self._parameters[self.DEFAULTS][item]

        else:
            super(InheritableCfgItem, self).__delitem__(item)

    def __iter__(self):
        return iter(self.inheritable_parameters)

    def __len__(self):
        return len(self.inheritable_parameters)
