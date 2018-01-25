import unittest
from uuid import uuid4

from .base_models import BaseModel, BaseModelWithEnum, BaseEnum, BaseModelWithListLinkField


class ModelBaseConvertationTest(unittest.TestCase):

    def test_enum_field(self) -> None:
        test_field_text = 'cute panda'
        base_model_record = BaseModelWithEnum(enum_field=BaseEnum.first, test_field=test_field_text)
        base_model_dict = base_model_record.to_dict()
        self.assertEqual(base_model_dict['test_field'], test_field_text)
        self.assertEqual(base_model_dict['enum_field'], BaseEnum.first.value)

    def test_list_link_field(self) -> None:
        c1_uuid = str(uuid4())
        c2_uuid = str(uuid4())
        c1_record = BaseModel(id_=c1_uuid, test_field_1='5', test_field_2='6')
        c2_record = BaseModel(id_=c2_uuid, test_field_1='5', test_field_2='6')
        check_model = BaseModelWithListLinkField(test_field='7')
        # Test initial set without get
        check_model = BaseModelWithListLinkField(test_field='7')
        check_model.link_list_field = [c1_record, c2_record]
        self.assertEqual(len(check_model.link_list_field), 2)
        check_model_dict = check_model.to_dict()
        self.assertEqual(check_model_dict['test_field'], '7')
        self.assertEqual(check_model_dict['link_list_field'], [c1_uuid, c2_uuid])
        # Test initial field usage
        check_model = BaseModelWithListLinkField(test_field='7')
        check_model.link_list_field.append(c1_record)
        check_model.link_list_field.append(c2_record)
        check_model_dict = check_model.to_dict()
        self.assertEqual(check_model_dict['test_field'], '7')
        self.assertEqual(check_model_dict['link_list_field'], [c1_uuid, c2_uuid])
        # Test field override
        check_model.link_list_field = [c1_record, c2_record]
        self.assertEqual(len(check_model.link_list_field), 2)
        check_model_dict = check_model.to_dict()
        self.assertEqual(check_model_dict['test_field'], '7')
        self.assertEqual(check_model_dict['link_list_field'], [c1_uuid, c2_uuid])
