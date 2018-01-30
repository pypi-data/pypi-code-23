import traceback

from .core import Field, FieldDescriptor, FieldGroup, SimpleField
from .core.enums import FieldKind, ValueStatus

class ChannelsNamesField(SimpleField):
    def __init__(self,
                 document):
        super(ChannelsNamesField, self).__init__(database_object=document,
                                                 aspect='distribution_channels.*',
                                                 field_locator='distribution_channels.channels',
                                                 kind = FieldKind.readonly)

    def _parse_value(self,
                     value):
        res = list(value.keys())
        res.remove('RIGHTS')
        return res

class DistributionChannelGroup(FieldGroup):
    def __init__(self,
                 document,
                 name):
        super(DistributionChannelGroup, self).__init__(document)
        self._fields['blocked'] = SimpleField(database_object=document,
                                              aspect='distribution_channels.*',
                                              dtype=bool,
                                              field_locator='distribution_channels.channels.'+name+'.blocked')

    blocked = FieldDescriptor('blocked')

class DistributionChannelsField(FieldGroup):
    def __init__(self,
                 document):
        super(DistributionChannelsField, self).__init__(document)
        

        self._fields['_channels_names'] = ChannelsNamesField(document)

        self._channels = {}
        
    _channels_names = FieldDescriptor('_channels_names')

    @property
    def value(self):
        return self

    def hard_set(self,
                 value):
        pass


    def _create_channels(self):
        for name in self._channels_names:
            if name not in self._channels:
                self._channels[name] = DistributionChannelGroup(self.database_object,
                                                                name)
    
    def __getitem__(self,
                    key):
        self._create_channels()
        if key not in self._channels:
            raise ValueError('Process information of app "{0}" is not available!'.format(key))
        return self._channels[key].value
            
    def __len__(self):
        self._create_channels()
        return len(self._channels)

    def __iter__(self):
        self._create_channels()
        return iter(self._channels)

    def items(self):
        self._create_channels()
        return list(self._channels.items())

    def invalidate(self):
        super(DistributionChannelsField, self).invalidate()
        for channel in list(self._channels.values()):
            channel.invalidate()

    def update(self,
               gjp):
        super(DistributionChannelsField, self).update(gjp)
        if self._fields['_channels_names'].status == ValueStatus.soft:
            self._create_channels()
        for channel in list(self._channels.values()):
            channel.update(gjp)

    def gjp(self,
            gjp):
        super(DistributionChannelsField, self).gjp(gjp)
        for channel in list(self._channels.values()):
            channel.gjp(gjp)

    def flush(self):
        super(DistributionChannelsField, self).flush()
        for channel in list(self._channels.values()):
            channel.flush()
