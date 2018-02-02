# -*- coding: utf-8 -*-

from sqlalchemy import String, TypeDecorator
from .models import Sequence
from .constants import SEQUENCE_FIELD_DEFAULT_EXPANDERS


# 这里面的初始化的时候的部分属性，我研究了好久，也每看出是干啥的来，
class SequenceField(TypeDecorator):
    """ Stores sequence values based on templates. """
    impl = String

    def __init__(self, *args, **kwargs):
        self.length = int(kwargs.get("length",50))
        if kwargs.get('key'):
            self.key = kwargs.pop('key')
            default_template = Sequence.get_template_by_key(self.key)
            self.template = kwargs.pop('template', default_template)
            Sequence.create_if_missing(self.key, self.template)
            # 默认的数据模板解释器
            default_expanders = SEQUENCE_FIELD_DEFAULT_EXPANDERS
            # 模板中需要替换的参数
            self.params = kwargs.pop('params', {})
            self.expanders = kwargs.pop('expanders', default_expanders)
            # 控制是否自动生成，如果为FASLE这个sequence就不会自动生成
            self.auto = kwargs.pop('auto', False)
            super(SequenceField, self).__init__(*args, **kwargs)

    def load_dialect_impl(self, dialect):
        return dialect.type_descriptor(String(self.length))

    def _next_value(self):
        # 根据key查询是否是已经创建过的序列，主要目的是取得关键性的数据
        seq = Sequence.create_if_missing(self.key, self.template)
        return seq.next_value(self.template, self.params, self.expanders)

    def process_bind_param(self, value, dialect):
        if self.auto and not value:
            sequence_string = self._next_value()
            return sequence_string
        elif self.auto and isinstance(value, dict):
            self.params = value
            self.key = str(value)
            sequence_string = self._next_value()
            return sequence_string
        else:
            return value

    def process_result_value(self, value, dialect):
        return value
