from pythonic_testcase import PythonicTestCase
from .. import ValueObject

class ValueObjectTest(PythonicTestCase):
    def test_should_set_values_in_dictionary(self):
        value_object = ValueObject()
        marker = object()
        value_object.fnord = marker
        self.assert_equals(marker, value_object['fnord'])
    
    def test_should_be_comparable_to_dictionary(self):
        value_object = ValueObject()
        value_object.fnord = "23"
        dictionary = dict()
        dictionary['fnord'] = "23"
        self.assert_equals(dictionary, value_object)
    
    def test_should_get_values_from_dictionary(self):
        marker = object()
        value_object = ValueObject()
        value_object['fnord'] = marker
        self.assert_equals(marker, value_object.fnord)
    
    def test_should_return_value_object_as_copy(self):
        copy = ValueObject().copy()
        self.assert_isinstance(copy, ValueObject)

    def test_should_return_value_object_as_deep_copy(self):
        deep_copy = ValueObject().deep_copy()
        self.assert_isinstance(deep_copy, ValueObject)

    def test_should_return_equal_object_as_deep_copy(self):
        original = ValueObject(fnord="bar")
        deep_copy = original.deep_copy()
        self.assert_equals(original, deep_copy)

    def test_should_copy_attributes_for_deep_copy(self):
        original = ValueObject(fnord=[1])
        deep_copy = original.deep_copy()
        deep_copy.fnord.append(2)
        self.assert_not_equals(original.fnord, deep_copy.fnord)
