from datetime import datetime
import uuid
import copy


class Serializer():

    def dump(self, origin_instance):
        return self.typping(origin_instance)

    def cycling(self, instance):

        if isinstance(instance, (set, list)):
            m_list = []
            for item in instance:
                value = self.typping(item)
                m_list.append(value)
            return m_list
        if isinstance(instance, dict):
            m_dict = {}
            for item in instance:
                value = self.typping(instance[item])
                m_dict.update({item: value})
            return m_dict

    def typping(self, instance):

        if isinstance(instance, set):
            return self.cycling(instance)
        elif isinstance(instance, list):
            return self.cycling(instance)
        elif isinstance(instance, dict):
            return self.cycling(instance)
        elif isinstance(instance, (float, int, str, bytes, bool, uuid.UUID)):
            return instance
        elif isinstance(instance, datetime):
            return instance
        elif instance is None:
            return None
        else:
            return self.typping(self.mapping(instance))

    def mapping(self, instance):
        return self.get_attr_dict(instance)

    def get_attr_dict(self, instance):
        try:
            exclude = [e for e in instance.__exclude__]
        except:
            exclude = []
        full = dict([[e, getattr(instance, e)] for e in dir(instance)
                     if not e.startswith('_') and not hasattr(
                         getattr(instance, e), '__call__') and e not in exclude])
        propery = dict([[p, getattr(instance, e).__get__(instance, type(instance))]
                        for p in full if hasattr(full[p], 'fset')])
        full.update(propery)
        return full

serializer = Serializer()
