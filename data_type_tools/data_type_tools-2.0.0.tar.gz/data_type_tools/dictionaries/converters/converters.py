import collections
import data_type_tools.shared.converters.interfaces


class DictionaryToNamedTupleConverter(data_type_tools.shared.converters.interfaces.ConverterInterface):
    def __init__(self, name='NamedTuple'):
        self.name = name

    def convert(self, dictionary):
        def handle_dictionaries():
            dictionary[key] = self.convert(dictionary_item_value)

        def handle_lists():
            for list_item in dictionary_item_value:
                list_items_index = dictionary_item_value.index(list_item)
                if type(list_item) in [str, int, float]:
                    dictionary[key][list_items_index] = list_item
                elif isinstance(list_item, dict):
                    dictionary[key][list_items_index] = self.convert(list_item)

        if isinstance(dictionary, dict):
            for key, dictionary_item_value in dictionary.items():
                if isinstance(dictionary_item_value, dict):
                    handle_dictionaries()
                if isinstance(dictionary_item_value, list):
                    handle_lists()
        return collections.namedtuple(self.name, dictionary.keys())(**dictionary)

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, name):
        self.check_is_string_instance(name)
        self._name = name

    def check_is_string_instance(self, name):
        if not isinstance(name, str):
            raise ValueError()
