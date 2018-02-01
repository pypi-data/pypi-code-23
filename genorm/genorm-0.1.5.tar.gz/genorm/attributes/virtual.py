import datetime
from ..exceptions import OrmTypeError, OrmParameterError
from ..manage import manager
from ..mapper import mapper
from ..utils import gettext
from .base import DataAttributeAbstract, VirtualAttributeAbstract
from .derived import Integer, BigInteger, Float, BigFloat, Date, Time, DateTime, String, CaptionString, \
    UuidPrimaryKey, Dimensions2D, ColumnTextAbstract
from ..values import ValueInterval, ValueList, ValueDict, ValueMatrix, ValueFileAttachment, ValuePictureAttachment, \
    ValueFiles, ValuePictures, ValueSet, ValueInlineSet


ATTACH_BY_MOVE = 'move'
ATTACH_BY_LINK = 'link'
ATTACH_BY_COPY = 'copy'


class Interval(VirtualAttributeAbstract):
    def __init__(self, low_attr, high_attr, min_value=None, max_value=None, **kwargs):
        super(Interval, self).__init__(**kwargs)
        self.virtual = True
        self.enumerable_value = True
        self.min_value = min_value
        self.max_value = max_value
        self._low_attr = low_attr
        self._high_attr = high_attr
        self.k_low = None
        self.k_high = None
        self.childs_type = None

    def on_declare(self):
        if not isinstance(self._low_attr, DataAttributeAbstract) \
                or not isinstance(self._high_attr, DataAttributeAbstract):
            raise OrmTypeError(
                "Interval attribute requires first and second parameters to be a type of data attribute!"
            )
        self.k_low = self._low_attr.model_k
        self.k_high = self._high_attr.model_k
        if self._low_attr.data_type != self._high_attr.data_type:
            raise OrmTypeError(
                "Interval attribute requires that both low and high attributes be the same type!"
            )
        if self._low_attr.data_type not in ('int', 'float', 'date', 'time', 'datetime') \
                or self._high_attr.data_type not in ('int', 'float', 'date', 'time', 'datetime'):
            raise OrmTypeError(
                "Interval attribute supports only numeric or date/time values!"
            )
        self.childs_type = self._low_attr.data_type
        self.attributes = self.k_low, self.k_high

    def initialize(self, instance, k):
        virtual_value = ValueInterval()
        virtual_value.model_k = k
        virtual_value.instance = instance
        virtual_value.c = self
        instance.__setattrabs__(k, virtual_value)


class TypedIntervalAbstract(Interval):
    def __init__(self, c_type, min_value=None, max_value=None, k_low=None, k_high=None, **kwargs):
        super(TypedIntervalAbstract, self).__init__(None, None, min_value=min_value, max_value=max_value, **kwargs)
        self.childs_attr_type = c_type
        self.k_low = k_low
        self.k_high = k_high

    def on_declare(self):
        k_low = self.k_low or "%s__low" % self.model_k
        k_high = self.k_high or "%s__high" % self.model_k
        while hasattr(self.model, k_low) or hasattr(self.model, k_high):
            k_low += '_'
            k_high += '_'
        c_low = self.childs_attr_type(nullable=self.nullable)
        c_high = self.childs_attr_type(nullable=self.nullable)
        setattr(self.model, k_low, c_low)
        setattr(self.model, k_high, c_high)
        self._low_attr = c_low
        self._high_attr = c_high
        self.k_low = k_low
        self.k_high = k_high
        super(TypedIntervalAbstract, self).on_declare()


class IntInterval(TypedIntervalAbstract):
    def __init__(self, min_value=None, max_value=None, k_low=None, k_high=None, **kwargs):
        super(IntInterval, self).__init__(Integer, min_value, max_value, k_low, k_high, **kwargs)


class FloatInterval(TypedIntervalAbstract):
    def __init__(self, min_value=None, max_value=None, k_low=None, k_high=None, **kwargs):
        super(FloatInterval, self).__init__(Float, min_value, max_value, k_low, k_high, **kwargs)


class BigIntInterval(TypedIntervalAbstract):
    def __init__(self, min_value=None, max_value=None, k_low=None, k_high=None, **kwargs):
        super(BigIntInterval, self).__init__(BigInteger, min_value, max_value, k_low, k_high, **kwargs)


class BigFloatInterval(TypedIntervalAbstract):
    def __init__(self, min_value=None, max_value=None, k_low=None, k_high=None, **kwargs):
        super(BigFloatInterval, self).__init__(BigFloat, min_value, max_value, k_low, k_high, **kwargs)


class DateInterval(TypedIntervalAbstract):
    def __init__(self, min_value=None, max_value=None, k_low=None, k_high=None, **kwargs):
        super(DateInterval, self).__init__(Date, min_value, max_value, k_low, k_high, **kwargs)


class TimeInterval(TypedIntervalAbstract):
    def __init__(self, min_value=None, max_value=None, k_low=None, k_high=None, **kwargs):
        super(TimeInterval, self).__init__(Time, min_value, max_value, k_low, k_high, **kwargs)


class DateTimeInterval(TypedIntervalAbstract):
    def __init__(self, min_value=None, max_value=None, k_low=None, k_high=None, **kwargs):
        super(DateTimeInterval, self).__init__(DateTime, min_value, max_value, k_low, k_high, **kwargs)


class ArrayAbstract(VirtualAttributeAbstract):
    def __init__(self, **kwargs):
        super(ArrayAbstract, self).__init__(**kwargs)
        self.virtual = True
        self.enumerable_value = True
        self.value_class = None
        self.value_attr = None
        self.dict_key = None
        self.columns = None
        self.unique = False
        self.array_model = None
        self.in_composite_results = False

    def on_model_declared(self):
        child_attrs = dict()
        if self.dict_key is not None:
            child_attrs['_k_'] = self.dict_key
        for k in self.columns:
            child_attrs[k] = self.columns[k]
        self.array_model = mapper.define_attribute_model(self.model, self.model_k, child_attrs)

    def initialize(self, instance, k):
        virtual_value = self.value_class()
        virtual_value.model_k = k
        virtual_value.instance = instance
        virtual_value.c = self
        instance.__setattrabs__(k, virtual_value)

    def write(self, instance, key):
        virtual_value = getattr(instance, key)
        virtual_value.write()

    def log_repr(self, src, dst, instance=None):
        return gettext('Changed'), None


class List(ArrayAbstract):
    def __init__(self, column_attr, **kwargs):
        self.unique = bool(kwargs.pop('unique', False))
        super(List, self).__init__(**kwargs)
        self.value_class = ValueList
        self.columns = {'value': column_attr, 'pos': Integer(nullable=False, default=0)}


class Dict(ArrayAbstract):
    def __init__(self, key_attr, column_attr, **kwargs):
        super(Dict, self).__init__(**kwargs)
        self.value_class = ValueDict
        self.dict_key = key_attr
        self.columns = {'_v_': column_attr}


class Matrix(ArrayAbstract):
    def __init__(self, key_attr, columns, **kwargs):
        super(Matrix, self).__init__(**kwargs)
        self.value_class = ValueMatrix
        self.dict_key = key_attr
        self.columns = dict()
        if not columns or not isinstance(columns, dict):
            raise OrmParameterError(
                "Matrix attribute type requires 'columns' parameter to be set and be a type of (dict) with format"
                " {'<column_name>': <column_type>, ...}!"
            )
        self.columns = columns


class Set(ArrayAbstract):
    def __init__(self, options, length=255, **kwargs):
        kwargs['options'] = options
        super(Set, self).__init__(**kwargs)
        if not isinstance(options, dict):
            raise OrmParameterError("Set requires 'options' argument to be a type (dict)!")
        self.value_class = ValueSet
        self.columns = {'value': String(length, nullable=True, default=None)}


class InlineSet(ColumnTextAbstract):
    def __init__(self, options, **kwargs):
        kwargs['options'] = options
        kwargs['nullable'] = False
        super(InlineSet, self).__init__(**kwargs)
        self.enumerable_value = True
        self.value_class = ValueInlineSet

    def log_repr(self, src, dst, instance=None):
        return gettext('Changed'), None


class AttachmentAbstract(String):
    def __init__(self, **kwargs):
        kwargs['nullable'] = True
        kwargs['default'] = None
        self.storage = kwargs.pop('storage', None)
        self.tag = kwargs.pop('tag', False)
        self.push_rule = kwargs.pop('push_rule', ATTACH_BY_COPY)
        self.pull_rule = kwargs.pop('pull_rule', ATTACH_BY_COPY)
        self.check_existance = kwargs.pop('check_existance', True)
        if self.push_rule not in (ATTACH_BY_COPY, ATTACH_BY_LINK, ATTACH_BY_MOVE):
            raise OrmParameterError(
                "attachment rule can be one of ATTACH_BY_COPY, ATTACH_BY_LINK or ATTACH_BY_MOVE constant!"
            )
        if self.pull_rule not in (ATTACH_BY_COPY, ATTACH_BY_LINK, ATTACH_BY_MOVE):
            raise OrmParameterError(
                "attachment rule can be one of ATTACH_BY_COPY, ATTACH_BY_LINK or ATTACH_BY_MOVE constant!"
            )
        max_filename_length = kwargs.pop('max_filename_length', 1023)
        super(AttachmentAbstract, self).__init__(max_filename_length, **kwargs)
        self.in_composite_results = False

    def on_instance_load(self, instance):
        v = instance.__getattrabs__(self.model_k)
        v.on_instance_load()

    def on_after_delete(self, instance, hard=None):
        """ Deletes the attachment, if any attached, when instance been deleted. Not affecting when
        soft-deletion used. """
        if not hard:
            return
        iv = self.get_instance_value(instance)
        if not iv.is_attached:
            return
        iv.after_instance_deleted()

    def on_before_write(self, instance):
        if not instance.__existing__:
            return
        iv = getattr(instance, self.model_k)
        iv.before_instance_write()

    def on_after_write(self, instance):
        iv = getattr(instance, self.model_k)
        before_ = iv.filename
        iv.after_instance_write()
        after_ = iv.filename
        if before_ == after_:
            return
        # Need to update this instance because the file name been changed
        # after physical attaching to the storage and we need to store correct
        # value in the database instead of initial one.
        instance.write(attrs=[self.model_k, ])

    def push_file(self, *args, **kwargs):
        """ Virtual. Real method is defined in the 'ValueFileAttachment' class. """
        pass

    def pull_file(self, *args, **kwargs):
        """ Virtual. Real method is defined in the 'ValueFileAttachment' class. """
        pass

    def remove_file(self, *args, **kwargs):
        """ Virtual. Real method is defined in the 'ValueFileAttachment' class. """
        pass

    @property
    def abs_path(self):
        """ Virtual. Real method is defined in the 'ValueFileAttachment' class. """
        return None

    @property
    def rel_path(self):
        """ Virtual. Real method is defined in the 'ValueFileAttachment' class. """
        return None

    @property
    def is_attached(self):
        """ Virtual. Real method is defined in the 'ValueFileAttachment' class. """
        return None


class FileAttachment(AttachmentAbstract):
    def __init__(self, **kwargs):
        super(FileAttachment, self).__init__(**kwargs)
        self.value_class = ValueFileAttachment

    def on_declare(self):
        if self.tag is False:
            self.tag = self.model.__meta__.tag
        if self.storage is None:
            self.storage = manager.get_default_file_storage(tag=self.tag)


class PictureAttachment(AttachmentAbstract):
    def __init__(self, **kwargs):
        self.max_width = kwargs.pop('max_width', None)
        self.min_width = kwargs.pop('min_width', None)
        self.max_height = kwargs.pop('max_height', None)
        self.min_height = kwargs.pop('min_height', None)
        self.image_format = kwargs.pop('image_format', 'JPEG')
        super(PictureAttachment, self).__init__(**kwargs)
        self.value_class = ValuePictureAttachment

    def on_declare(self):
        if self.tag is False:
            self.tag = self.model.__meta__.tag
        if self.storage is None:
            self.storage = manager.get_default_picture_storage(tag=self.tag)

    def push_image(self, *args, **kwargs):
        """ Virtual. Real method is defined in the 'ValuePictureAttachment' class. """
        pass

    def push_image_to(self, *args, **kwargs):
        """ Virtual. Real method is defined in the 'ValuePictureAttachment' class. """
        pass

    def pull_image_to(self, *args, **kwargs):
        """ Virtual. Real method is defined in the 'ValuePictureAttachment' class. """
        pass

    def pull_image(self, *args, **kwargs):
        """ Virtual. Real method is defined in the 'ValuePictureAttachment' class. """
        pass

    def remove_image(self, *args, **kwargs):
        """ Virtual. Real method is defined in the 'ValuePictureAttachment' class. """
        pass


class FilesAbstract(VirtualAttributeAbstract):
    def __init__(self, **kwargs):
        self.storage = kwargs.pop('storage', None)
        self.tag = kwargs.pop('tag', False)
        self.push_rule = kwargs.pop('push_rule', ATTACH_BY_COPY)
        self.pull_rule = kwargs.pop('pull_rule', ATTACH_BY_COPY)
        if self.push_rule not in (ATTACH_BY_COPY, ATTACH_BY_LINK, ATTACH_BY_MOVE):
            raise OrmParameterError(
                "attachment rule can be one of ATTACH_BY_COPY, ATTACH_BY_LINK or ATTACH_BY_MOVE constant!"
            )
        if self.pull_rule not in (ATTACH_BY_COPY, ATTACH_BY_LINK, ATTACH_BY_MOVE):
            raise OrmParameterError(
                "attachment rule can be one of ATTACH_BY_COPY, ATTACH_BY_LINK or ATTACH_BY_MOVE constant!"
            )
        self.max_filename_length = kwargs.pop('max_filename_length', 1023)
        self.extra_attrs = kwargs.pop('extra_attrs', None)
        super(FilesAbstract, self).__init__(**kwargs)
        self.virtual = True
        self.enumerable_value = True
        self.in_composite_results = False
        self.value_class = None
        self.array_model = None
        self.array_model_attrs = {
            'id': UuidPrimaryKey(),
            'time_created': DateTime(nullable=False, default=datetime.datetime.now, caption=gettext('Created')),
            'title': CaptionString(caption=gettext('Name')),
            'filesize': Integer(nullable=False, default=0, caption=gettext('Size'))
        }
        self.array_model_attrs['id'].declaration_order = 0
        if self.extra_attrs is not None and not isinstance(self.extra_attrs, dict):
            raise OrmParameterError("Files|Pictures attribute's 'extra_attrs' must be of type (dict)!")
        elif self.extra_attrs is not None:
            for k in self.extra_attrs:
                self.array_model_attrs[k] = self.extra_attrs[k]

    def __setattr__(self, key, value):
        if key in ('push_rule', 'pull_rule', 'max_filename_length', 'max_width', 'min_width', 'max_height',
                   'min_height', 'image_format', 'storage'):
            array_model = getattr(self, 'array_model', None)
            if array_model is not None:
                setattr(array_model.attachment, key, value)
        super(FilesAbstract, self).__setattr__(key, value)

    def on_model_declared(self):
        self.array_model = mapper.define_attribute_model(self.model, self.model_k, self.array_model_attrs)

    def initialize(self, instance, k):
        virtual_value = self.value_class()
        virtual_value.model_k = k
        virtual_value.instance = instance
        virtual_value.c = self
        instance.__setattrabs__(k, virtual_value)

    def write(self, instance, key):
        virtual_value = getattr(instance, key)
        virtual_value.write()

    def on_after_delete(self, instance, hard=None):
        """ Deletes the attachment, if any attached, when instance been deleted. Not affecting when
        soft-deletion used. """
        if not hard:
            return
        iv = self.get_instance_value(instance)
        if not iv.is_attached:
            return
        iv.after_parent_instance_deleted()

    def log_repr(self, src, dst, instance=None):
        return gettext('Changed'), None


class Files(FilesAbstract):
    def __init__(self, **kwargs):
        super(Files, self).__init__(**kwargs)
        self.value_class = ValueFiles
        self.array_model_attrs['attachment'] = FileAttachment(caption=gettext('File'),
                                                              storage=self.storage,
                                                              tag=self.tag,
                                                              push_rule=self.push_rule,
                                                              pull_rule=self.pull_rule,
                                                              max_filename_length=self.max_filename_length,
                                                              check_existance=False)


class Pictures(FilesAbstract):
    def __init__(self, **kwargs):
        self.max_width = kwargs.pop('max_width', None)
        self.min_width = kwargs.pop('min_width', None)
        self.max_height = kwargs.pop('max_height', None)
        self.min_height = kwargs.pop('min_height', None)
        self.image_format = kwargs.pop('image_format', None)
        super(Pictures, self).__init__(**kwargs)
        self.value_class = ValuePictures
        self.array_model_attrs['attachment'] = PictureAttachment(caption=gettext('Picture'),
                                                                 storage=self.storage,
                                                                 tag=self.tag,
                                                                 max_filename_length=self.max_filename_length,
                                                                 max_width=self.max_width,
                                                                 min_width=self.min_width,
                                                                 max_height=self.max_height,
                                                                 min_height=self.min_height,
                                                                 image_format=self.image_format,
                                                                 check_existance=False)
        self.array_model_attrs['dimensions'] = Dimensions2D(nullable=False, caption='Dimensions')
        self.array_model_attrs['format'] = String(16, nullable=False, default='', caption=gettext('Format'))




