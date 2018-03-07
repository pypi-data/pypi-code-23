# encoding: utf-8

from copy import deepcopy
from collections import MutableMapping
from future.utils import python_2_unicode_compatible, iteritems


@python_2_unicode_compatible
class CfgItem(MutableMapping):

    def __init__(self,
                 cfg_fn,
                 cfg_root,
                 key,
                 key_name=None,
                 **overrides):

        """
        :param cfg_fn:          Function that retrieves the config object
                                for this item
        :param cfg_root:        Root config key to use for this config.
        :param key:             item key.
        :param key_name:        key name for the object from parameters
        """

        # As we have implemented __setattr__ we have to call the base classes
        # __setattr__ to set instance params otherwise we get infinite recursion!

        # Setup required parameters for saving config
        super(CfgItem, self).__setattr__('_cfg', cfg_fn())
        super(CfgItem, self).__setattr__('_cfg_fn', cfg_fn)
        super(CfgItem, self).__setattr__('_cfg_root', cfg_root)
        super(CfgItem, self).__setattr__('_key_attr', key)
        super(CfgItem, self).__setattr__('_key_name', key_name)

        # Save any passed overrides
        super(CfgItem, self).__setattr__('_overrides', overrides)

        # Setup our parameters dict
        super(CfgItem, self).__setattr__('_parameters', self.raw_items)

        # Save our current key value
        super(CfgItem, self).__setattr__('_original_key_value', key)

    @property
    def raw_items(self):
        items = self._cfg[self._full_key]

        # Return a copy so that modifications of the retrieved do not get saved in config unless explicitly requested!
        return deepcopy(items)

    @property
    def _full_key(self):
        return u'{c}.{i}'.format(c=self._cfg_root,
                                 i=self._key_attr)

    @property
    def key(self):
        return self._key_attr

    @property
    def overrides(self):
        return self._overrides

    @property
    def parameters(self):

        if self._parameters is None:
            super(CfgItem, self).__setattr__('_parameters', {})

        if self._key_name is not None:
            self._parameters[self._key_name] = self._key_attr

        return self._apply_override(self._parameters)

    def _apply_override(self,
                        params):

        # TODO: Add more detailed tests for overrides (SAVE IS IMPORTANT HERE!)

        overridden_params = {}

        for param, value in iter(params.items()):
            try:
                overridden_params[param] = deepcopy(value)
            except:
                print(u'could not copy "{param}. Using reference to {object}"'
                      .format(param=param,
                              object=value))
                overridden_params[param] = value

        for key, value in iteritems(self.overrides):
            overridden_params[key] = value

        return overridden_params

    def save_changes(self):

        updated_item = deepcopy(self.parameters)

        # check whether this is a key change
        if self._original_key_value != self._key_attr:
            # it is so remove the original key
            original_key = u'{c}.{d}'.format(c=self._cfg_root,
                                             d=self._original_key_value)
            del self._cfg[original_key]

        # Remove key name parameter
        if self._key_name is not None and self._key_name in updated_item:
            del updated_item[self._key_name]

        self._cfg[self._full_key] = updated_item

    def __str__(self):
        return u'\n'.join(u'{key}: {value}'.format(key=key,
                                                   value=self[key])
                          for key in sorted(iter(self)))

    def __getitem__(self, item):
        return self.parameters[item]

    def __getattr__(self, item):
        try:
            return self.__getitem__(item)

        except KeyError:
            raise AttributeError(u'{name} does not have attribute {i}'.format(name=self.__class__.__name__,
                                                                              i=item))

    def __setitem__(self, item, value):

        if self._key_name is not None and item == self._key_name:
            self._key_attr = value

        else:
            self._parameters[item] = value

    def __setattr__(self, key, value):
        if key in self.__dict__:
            super(CfgItem, self).__setattr__(key, value)

        else:
            self.__setitem__(key, value)

    def __delitem__(self, item):
        del self._parameters[item]

    def __delattr__(self, item):
        if item in self.__dict__:
            super(CfgItem, self).__delattr__(item)

        else:
            self.__delitem__(item)

    def __iter__(self):
        return iter(self.parameters)

    def __len__(self):
        return len(self.parameters)
