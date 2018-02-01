import os
import os.path
import shutil
import math
from .base import AttributeValueVirtual, AttributeValueNull
from ..exceptions import OrmValueError, OrmNotDefinedYet, OrmParameterError, \
    OrmAttachmentAlreadyExists, OrmAttachmentNotExists
from ..utils import gettext


class ValueAttachmentAbstract(AttributeValueVirtual):
    basecls = False
    check_modified = True

    def __init__(self, value):
        super(ValueAttachmentAbstract, self).__init__()
        self._attachment = None
        self._on_write = False
        self._value = value
        self._need_write = False
        self.parent_instance = None
        self.parent_k = None
        self.attributes_instance = None

    def __repr__(self):
        return "<Not attached>" if not self.is_attached else "Attachment(%s)" % self._value

    def base(self, value):
        return None if value is None or isinstance(value, AttributeValueNull) else str(value)

    @property
    def value(self):
        return self._value

    @property
    def string(self):
        return str(self._value) if self.is_attached else ""

    def _get_c(self):
        return getattr(self.instance.__class__, self.model_k) if self.model_k is not None else None

    def get_value(self):
        return self

    @property
    def _instance(self):
        return self.instance if not self.parent_instance else self.parent_instance

    @property
    def _attr_name(self):
        return self.model_k if not self.parent_k else self.parent_k

    @property
    def is_attached(self):
        return self._value is not None

    def set_value(self, instance, key, value):
        before_ = self._value
        if isinstance(value, ValueAttachmentAbstract):
            self._value = value.value
            return self._value, before_
        if value is None or isinstance(value, AttributeValueNull):
            self._value = None
            return None, before_
        if not isinstance(value, str):
            raise OrmValueError("single attachments can be directly set specifying (str) file name in the storage!")
        self._value = value
        self._attachment = self.abs_path
        return self._value, before_

    def verify_storage_existance(self):
        if self._value is None:
            return True
        c = self._get_c()
        if c is None:
            raise OrmNotDefinedYet("cannot deal with attachments until model been defined!")
        r = c.storage.verify_file_existance(self._instance, self._attr_name, self._value)
        if not r:
            self._value = None
        return r

    def _check_not_attached(self):
        if self.is_attached:
            raise OrmAttachmentAlreadyExists(self._attr_name)

    def _check_attached(self):
        if not self.is_attached:
            raise OrmAttachmentNotExists(self._attr_name)

    def _execute_on_write(self):
        if self._on_write is False:
            return
        if not isinstance(self._on_write, (list, tuple)):
            return
        f = self._on_write[0]
        args = self._on_write[1] if len(self._on_write) >= 2 else list()
        kwargs = self._on_write[2] if len(self._on_write) >= 3 else dict()
        self._on_write = False
        r = f(*args, **kwargs)
        if r is None:
            return
        self._value = r if not isinstance(r, (list, tuple)) else r[0]

    def before_instance_write(self):
        if not self._need_write:
            return
        if not self._instance.__existing__:
            return
        self._execute_on_write()
        self._need_write = False
        self._attachment = None

    def after_instance_write(self):
        if not self._need_write:
            return
        self._execute_on_write()
        self._need_write = False
        self._attachment = None

    def after_instance_deleted(self):
        if not self.is_attached:
            return
        c = self._get_c()
        if c is None:
            raise OrmNotDefinedYet("cannot deal with attachments until model been defined!")
        c.storage.del_file(self._instance, self._attr_name, str(self._value))

    def on_instance_load(self):
        c = self._get_c()
        if c is None:
            raise OrmNotDefinedYet("cannot deal with attachments until model been defined!")
        if c.check_existance:
            self.verify_storage_existance()

    def push_file(self, src, filename=None, rule=None):
        from ..attributes.virtual import ATTACH_BY_COPY, ATTACH_BY_MOVE, ATTACH_BY_LINK
        c = self._get_c()
        if c is None:
            raise OrmNotDefinedYet("cannot deal with attachments until model been defined!")
        # self._check_not_attached()
        rule = rule or c.push_rule
        if rule not in (ATTACH_BY_COPY, ATTACH_BY_LINK, ATTACH_BY_MOVE):
            raise OrmParameterError(
                "attachment rule can be one of ATTACH_BY_COPY, ATTACH_BY_LINK or ATTACH_BY_MOVE constant!"
            )
        if rule == ATTACH_BY_COPY:
            self._copy_file_from(src, filename)
        elif rule == ATTACH_BY_LINK:
            self._link_file_from(src, filename)
        else:
            self._move_file_from(src, filename)

    def remove_file(self):
        c = self._get_c()
        if c is None:
            raise OrmNotDefinedYet("cannot deal with attachments until model been defined!")
        self._check_attached()
        self._on_write = c.storage.del_file, (self._instance, self._attr_name, str(self._value))
        self._value = None
        self._attachment = None
        self._need_write = True
        self.instance.__changes__[self.model_k] = (gettext('Detached', 'attachments'), None)
        if self._instance != self.instance:
            self._instance.__changes__[self._attr_name] = (gettext('Detached', 'attachments'), None)

    def pull_file(self, dst, rule=None):
        from ..attributes.virtual import ATTACH_BY_COPY, ATTACH_BY_MOVE, ATTACH_BY_LINK
        c = self._get_c()
        if c is None:
            raise OrmNotDefinedYet("cannot deal with attachments until model been defined!")
        rule = rule or c.pull_rule
        if rule not in (ATTACH_BY_COPY, ATTACH_BY_LINK, ATTACH_BY_MOVE):
            raise OrmParameterError(
                "attachment rule can be one of ATTACH_BY_COPY, ATTACH_BY_LINK or ATTACH_BY_MOVE constant!"
            )
        if rule == ATTACH_BY_COPY:
            self._copy_file_to(dst)
        elif rule == ATTACH_BY_LINK:
            self._link_file_to(dst)
        else:
            self._move_file_to(dst)

    def _push_on_write_file(self, f, src, filename):
        fn, fp = f(src, self._instance, self._attr_name, filename)
        self._value = fn
        self.instance.__changes__[self.model_k] = ("%s '%s'" % (gettext('Attached', 'attachments'), fn), None)
        if self._instance != self.instance:
            self._instance.__changes__[self._attr_name] = ("%s '%s'" % (gettext('Attached', 'attachments'), fn), None)
        if self.attributes_instance is not None:
            setattr(self.attributes_instance, 'filesize', int(math.ceil(float(os.stat(fp).st_size) / 1024.0)))

    def _copy_file_from(self, src, filename=None):
        c = self._get_c()
        if c is None:
            raise OrmNotDefinedYet("cannot deal with attachments until model been defined!")
        self._value = c.storage.suggest_filename(self._instance, self._attr_name, filename or src)
        self._on_write = self._push_on_write_file, (c.storage.copy_file_from, src, str(self._value))
        self._need_write = True
        self._attachment = src
        self.instance.__changes__[self.model_k] = (gettext('Attached', 'attachments'), None)
        if self._instance != self.instance:
            self._instance.__changes__[self._attr_name] = (gettext('Attached', 'attachments'), None)

    def _link_file_from(self, src, filename=None):
        c = self._get_c()
        if c is None:
            raise OrmNotDefinedYet("cannot deal with attachments until model been defined!")
        self._value = c.storage.suggest_filename(self.instance, self.model_k, filename or src)
        self._on_write = self._push_on_write_file, (c.storage.link_file_from, src, str(self._value))
        self._need_write = True
        self._attachment = src
        self.instance.__changes__[self.model_k] = (gettext('Attached', 'attachments'), None)
        if self._instance != self.instance:
            self._instance.__changes__[self._attr_name] = (gettext('Attached', 'attachments'), None)

    def _move_file_from(self, src, filename=None):
        c = self._get_c()
        if c is None:
            raise OrmNotDefinedYet("cannot deal with attachments until model been defined!")
        self._value = c.storage.suggest_filename(self.instance, self.model_k, filename or src)
        self._on_write = self._push_on_write_file, (c.storage.move_file_from, src, str(self._value))
        self._need_write = True
        self._attachment = src
        self.instance.__changes__[self.model_k] = (gettext('Attached', 'attachments'), None)
        if self._instance != self.instance:
            self._instance.__changes__[self._attr_name] = (gettext('Attached', 'attachments'), None)

    def _move_file_to(self, dst):
        c = self._get_c()
        if c is None:
            raise OrmNotDefinedYet("cannot deal with attachments until model been defined!")
        self._check_attached()
        if dst[-1] == '/':
            dst += self._value
        if not self._need_write:
            c.storage.link_file_to(dst, self._instance, self._attr_name)
        else:
            if not os.path.lexists(self._attachment):
                raise OrmAttachmentNotExists(self._attachment)
            os.link(self._attachment, dst)
        self.remove_file()

    def _copy_file_to(self, dst):
        c = self._get_c()
        if c is None:
            raise OrmNotDefinedYet("cannot deal with attachments until model been defined!")
        self._check_attached()
        if dst[-1] == '/':
            dst += self._value
        if not self._need_write:
            c.storage.copy_file_to(dst, self._instance, self._attr_name)
        else:
            if not os.path.lexists(self._attachment):
                raise OrmAttachmentNotExists(self._attachment)
            shutil.copyfile(self._attachment, dst)

    def _link_file_to(self, dst):
        c = self._get_c()
        if c is None:
            raise OrmNotDefinedYet("cannot deal with attachments until model been defined!")
        self._check_attached()
        if dst[-1] == '/':
            dst += self._value
        if not self._need_write:
            c.storage.link_file_to(dst, self._instance, self._attr_name)
        else:
            if not os.path.lexists(self._attachment):
                raise OrmAttachmentNotExists(self._attachment)
            os.link(self._attachment, dst)

    def rename(self, new_filename):
        # TODO!
        pass

    @property
    def rel_path(self):
        if not self.is_attached:
            return None
        c = self._get_c()
        if c is None:
            raise OrmNotDefinedYet("cannot deal with attachments until model been defined!")
        if self._need_write:
            return None
        return c.storage.get_relative_filepath(self._instance, self._attr_name, self._value)

    @property
    def abs_path(self):
        if not self.is_attached:
            return None
        c = self._get_c()
        if c is None:
            raise OrmNotDefinedYet("cannot deal with attachments until model been defined!")
        if self._need_write:
            return self._attachment
        return c.storage.get_absolute_filepath(self._instance, self._attr_name, self._value)

    @property
    def filename(self):
        return self._value


class ValueFileAttachment(ValueAttachmentAbstract):
    pass


class ValuePictureAttachment(ValueAttachmentAbstract):
    def __init__(self, value):
        super(ValuePictureAttachment, self).__init__(value)

    def _push_on_write_image(self, f, src, filename, kw):
        fn, fp, img = f(src, self._instance, self._attr_name, filename, **kw)
        self._value = fn
        self.instance.__changes__[self.model_k] = ("%s '%s'" % (gettext('Attached', 'attachments'), fn), None)
        if self._instance != self.instance:
            self._instance.__changes__[self._attr_name] = ("%s '%s'" % (gettext('Attached', 'attachments'), fn), None)
        if self.attributes_instance is not None:
            img_width, img_height = img.size
            setattr(self.attributes_instance, 'filesize', int(math.ceil(float(os.stat(fp).st_size) / 1024.0)))
            setattr(self.attributes_instance, 'dimensions', (img_width, img_height))
            setattr(self.attributes_instance, 'format', str(img.format))

    def remove_image(self):
        self.remove_file()

    def push_image(self, image, filename=None, **kwargs):
        c = self._get_c()
        if c is None:
            raise OrmNotDefinedYet("cannot deal with attachments until model been defined!")
        self._value = c.storage.suggest_filename(self._instance, self._attr_name, filename)
        self._on_write = self._push_on_write_image, (c.storage.push_image, image, str(self._value), kwargs)
        self._need_write = True
        self._attachment = image
        self.instance.__changes__[self.model_k] = (gettext('Attached', 'attachments'), None)
        if self._instance != self.instance:
            self._instance.__changes__[self._attr_name] = (gettext('Attached', 'attachments'), None)

    def push_image_from(self, src, filename=None, **kwargs):
        c = self._get_c()
        if c is None:
            raise OrmNotDefinedYet("cannot deal with attachments until model been defined!")
        self._value = c.storage.suggest_filename(self._instance, self._attr_name, filename)
        self._on_write = self._push_on_write_image, (c.storage.push_image_from, src, str(self._value), kwargs)
        self._need_write = True
        self._attachment = src
        self.instance.__changes__[self.model_k] = (gettext('Attached', 'attachments'), None)
        if self._instance != self.instance:
            self._instance.__changes__[self._attr_name] = (gettext('Attached', 'attachments'), None)

    def pull_image_to(self, dst):
        c = self._get_c()
        if c is None:
            raise OrmNotDefinedYet("cannot deal with attachments until model been defined!")
        self._check_attached()
        if dst[-1] == '/':
            dst += self._value
        if not self._need_write:
            c.storage.pull_image_to(dst, self._instance, self._attr_name)
        else:
            if isinstance(self._attachment, str):
                if not os.path.lexists(self._attachment):
                    raise OrmAttachmentNotExists(self._attachment)
                shutil.copyfile(self._attachment, dst)
            else:
                image_format = getattr(c.storage, 'image_format', None)
                quality = getattr(c.storage, 'quality', 100)
                if image_format is not None:
                    self._attachment.save(dst, image_format, quality=quality)
                else:
                    self._attachment.save(dst)

    def pull_image(self):
        from PIL import Image
        c = self._get_c()
        if c is None:
            raise OrmNotDefinedYet("cannot deal with attachments until model been defined!")
        self._check_attached()
        if not self._need_write:
            return c.storage.pull_image(self._instance, self._attr_name)
        else:
            if isinstance(self._attachment, str):
                if not os.path.lexists(self._attachment):
                    raise OrmAttachmentNotExists(self._attachment)
                return Image.open(self._attachment)
            else:
                return self._attachment

