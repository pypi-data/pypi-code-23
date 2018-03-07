# encoding: utf-8

from .cfg_item import CfgItem
from .cfg_items import CfgItems
from .inheritable_cfg_item import InheritableCfgItem


class ContainerItemDefaults(InheritableCfgItem):
    DEFAULTS = u'item_defaults'


class ContainerCfgItem(InheritableCfgItem):

    """ A Container Config class for Config items. """

    DEFAULTS = u'items'

    # Define how container inheritance should work.
    # If STRICT_ITEMS is True:
    #       A container will only surface defined `items`.
    # If STRICT_ITEMS is False:
    #       A container will surface all `items` defined in the actual
    #       items config not including hidden items.
    #       Note: Iteration is dramatically slower when STRICT_ITEMS is False.
    STRICT_ITEMS = True

    ITEMS = CfgItems
    ITEMS_INIT_PARAMS = {}

    ITEM_DEFAULTS_CLASS = ContainerItemDefaults

    def __init__(self,
                 *args,
                 **kwargs):
        super(ContainerCfgItem, self).__init__(*args, **kwargs)

        super(CfgItem, self).__setattr__('_item_defaults', self.ITEM_DEFAULTS_CLASS(cfg_fn=self._cfg_fn,
                                                                                    cfg_root=self._cfg_root,
                                                                                    key=self._key_attr))

        super(CfgItem, self).__setattr__('_items', self.ITEMS(**self.ITEMS_INIT_PARAMS))

    def __getitem__(self, item):

        try:
            # Get the overrides for requested item
            item_params = super(ContainerCfgItem, self).__getitem__(item)

        except KeyError:
            # We should not raise KeyError here as the item may exist, we just haven't
            # configured any overrides at the container level!
            item_params = {}

        if item_params is None:
            item_params = {}

        # Combine overrides into a single overrides dict.
        # Note: Item overrides take precedence over container overrides
        overrides = self._inherit(self._item_defaults.inheritable_parameters, item_params)

        # Create the item object
        # Note: If an override does exist but the item itself does not a KeyError will be raised.
        #       The container provides overrides for Items, it should NOT provide new Item definitions!
        item_obj = self._items.load_item(key=item,
                                         **overrides)

        # Return item object
        return item_obj

    def __iter__(self):
        if self.STRICT_ITEMS:
            return super(ContainerCfgItem, self).__iter__()

        else:
            return iter(item.key for item in iter(self._items))

    def __len__(self):
        if self.STRICT_ITEMS:
            return super(ContainerCfgItem, self).__len__()

        else:
            return len(self._items.get_items())

    def __str__(self):
        text = [
            u'{key}: '.format(key=self.key)
        ]

        pad = u' ' * 4

        for key in sorted(iter(self)):

            text.append(u'{pad}{key}: '.format(pad=pad,
                                               key=key))
            text.append(u'\n'.join([u'{pad}{value}'.format(pad=pad * 2,
                                                           value=line) for line in str(self[key]).splitlines()]))

        return u'\n'.join(text)
