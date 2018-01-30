import os.path
import uuid
import shutil
from .utils import remove_trailing_slash, fit_image
from .exceptions import OrmParameterError, OrmAttachmentNotExists, OrmAttachmentSourceNotExists, \
    OrmAttachmentAlreadyExists


class OrmStorageAbstract(object):
    """ A class used to define an actual files' placement - a storage. Storages are used to store
    files which beign attached to the objects outside database (as recommended behaviour). Files,
    which defines as a part of database object, are actually not besides in the database tables
    or its space, but instead they lays in the file system of the machine where this ORM
    is used at. """
    def __init__(self,
                 base_path,
                 with_model=True,
                 with_objpk=True,
                 with_attrname=True,
                 uuid_names=False,
                 prefix=None,
                 suffix=None,
                 allowed_ext=None,
                 prohibited_ext=None,
                 autoname=True):
        if not isinstance(base_path, str):
            raise OrmParameterError("storage 'base_path' must be a type of (str)!")
        if prefix is not None and not isinstance(prefix, str):
            raise OrmParameterError("storage's 'prefix' must be a type of (str) or not set!")
        if suffix is not None and not isinstance(suffix, str):
            raise OrmParameterError("storage's 'suffix' must be a type of (str) or not set!")
        self._base_path = remove_trailing_slash(base_path)
        self.with_model = bool(with_model)
        self.with_objpk = bool(with_objpk)
        self.with_attrname = bool(with_attrname)
        self.uuid_names = bool(uuid_names)
        self.prefix = prefix
        self.suffix = suffix
        self.allowed_ext = allowed_ext
        self.prohibited_ext = prohibited_ext
        self.autoname = bool(autoname)

    @property
    def base_path(self):
        return self._base_path

    @base_path.setter
    def base_path(self, value):
        if not isinstance(value, str):
            raise OrmParameterError("storage 'base_path' must be a type of (str)!")
        self._base_path = remove_trailing_slash(value)

    def _compose_rel_path(self, instance, attr_name):
        d = list()
        if self.with_model:
            d.append(instance.__class__.__name__)
        if self.with_objpk:
            pk = instance.__class__.__meta__.primary_key
            vpk = list()
            for k in pk:
                vpk.append(str(getattr(instance, k)))
            d.append("@".join(vpk))
        if self.with_attrname:
            d.append(attr_name)
        return "/".join(d)

    def _compose_abs_path(self, instance, attr_name):
        return "/".join((self.base_path, self._compose_rel_path(instance, attr_name)))

    @staticmethod
    def _get_filename_from_attribute(instance, attr_name):
        # TODO ! special value classes for attachments
        # if self.uuid_names:
        #     return uuid.uuid4().hex
        return getattr(instance, attr_name).value

    def make_filename(self, instance, attr_name, filename=None, overwrite=False):
        filename = filename \
                   or (self._get_filename_from_attribute(instance, attr_name)
                       if not self.uuid_names
                       else uuid.uuid4().hex)
        if overwrite:
            return filename
        dirpath = self._compose_abs_path(instance, attr_name)
        f_name, f_ext = os.path.splitext(filename)
        filepath = "%s%s" % (f_name, f_ext)
        i = 1
        if os.path.lexists("%s/%s" % (dirpath, filepath)) and not self.autoname:
            raise OrmAttachmentAlreadyExists(
                "attachment file with name '%s' is already exists and 'autoname' set to False!" % filepath
            )
        while os.path.lexists("%s/%s" % (dirpath, filepath)):
            i += 1
            filepath = "%s (%i)%s" % (f_name, i, f_ext)
        return filepath

    def suggest_filename(self, instance, attr_name, filename=None, overwrite=False):
        if isinstance(filename, str) and '/' in filename:
            filename = os.path.basename(filename)
        filename = uuid.uuid4().hex \
            if self.uuid_names \
            else (filename if filename else self._get_filename_from_attribute(instance, attr_name))
        if overwrite:
            return filename
        dirpath = self._compose_abs_path(instance, attr_name)
        f_name, f_ext = os.path.splitext(filename)
        filepath = "%s%s" % (f_name, f_ext)
        i = 1
        if os.path.lexists("%s/%s" % (dirpath, filepath)) and not self.autoname:
            raise OrmAttachmentAlreadyExists(
                "attachment file with name '%s' is already exists and 'autoname' set to False!" % filepath
            )
        while os.path.lexists("%s/%s" % (dirpath, filepath)):
            i += 1
            filepath = "%s (%i)%s" % (f_name, i, f_ext)
        return filepath

    def copy_file_from(self, source, instance, attr_name, filename=None):
        """ Puts the file into the storage. File must exists. If filename is omitted - it
        will be taken from the source filename.
        This method copies file from the original source, not removing it's source. This might
        take a time to complete, depending on the size of the copying attachment file.
        @source                 Full path to the file which to put to the storage;
        @instance               The object instance which holds this file attachment;
        @attr_name              The name of the attribute of the given object instance which
                                represents the file attachment;
        @filename               Filename to set up (not required to be the same as original
                                filename of the file); if omitted - the filename of the
                                original file will be taken;
        """
        if not filename:
            filename = os.path.basename(source)
        filename = self.make_filename(instance, attr_name, filename)
        attachment_dir = self._compose_abs_path(instance, attr_name)
        if not os.path.isdir(attachment_dir):
            os.makedirs(attachment_dir)
        attachment_path = self.get_absolute_filepath(instance, attr_name, filename)
        if os.path.lexists(attachment_path):
            raise OrmAttachmentAlreadyExists(attachment_path)
        if not os.path.lexists(source):
            raise OrmAttachmentSourceNotExists(source)
        shutil.copyfile(source, attachment_path)
        return filename, attachment_path

    def link_file_from(self, source, instance, attr_name, filename=None):
        """ Puts the file into the storage. File must exists. If filename is omitted - it
        will be taken from the source filename.
        This method makes a hard link from the source file to the storage. Source file not
        removes, but both source file and attachment will point to the same block of file
        system, so any changes in the content of any of them will affect the other too.
        Note that this operation requires that both source file and attachment (storage)
        to be located in the same file system (mounted FS).
        @source                 Full path to the file which to put to the storage;
        @instance               The object instance which holds this file attachment;
        @attr_name              The name of the attribute of the given object instance which
                                represents the file attachment;
        @filename               Filename to set up (not required to be the same as original
                                filename of the file); if omitted - the filename of the
                                original file will be taken;
        """
        if not filename:
            filename = os.path.basename(source)
        filename = self.make_filename(instance, attr_name, filename)
        attachment_dir = self._compose_abs_path(instance, attr_name)
        if not os.path.isdir(attachment_dir):
            os.makedirs(attachment_dir)
        attachment_path = self.get_absolute_filepath(instance, attr_name, filename)
        if os.path.lexists(attachment_path):
            raise OrmAttachmentAlreadyExists(attachment_path)
        if not os.path.lexists(source):
            raise OrmAttachmentSourceNotExists(source)
        os.link(source, attachment_path)
        return filename, attachment_path

    def move_file_from(self, source, instance, attr_name, filename=None):
        """ Puts the file into the storage. File must exists. If filename is omitted - it
        will be taken from the source filename.
        This method moves file from the original file system position to the storage. Most
        often this is the preferred option because it is fast while source file and the
        storage are located at the same file system (mounted FS).
        @source                 Full path to the file which to put to the storage;
        @instance               The object instance which holds this file attachment;
        @attr_name              The name of the attribute of the given object instance which
                                represents the file attachment;
        @filename               Filename to set up (not required to be the same as original
                                filename of the file); if omitted - the filename of the
                                original file will be taken;
        """
        if not filename:
            filename = os.path.basename(source)
        filename = self.make_filename(instance, attr_name, filename)
        attachment_dir = self._compose_abs_path(instance, attr_name)
        if not os.path.isdir(attachment_dir):
            os.makedirs(attachment_dir)
        attachment_path = self.get_absolute_filepath(instance, attr_name, filename)
        if os.path.lexists(attachment_path):
            raise OrmAttachmentAlreadyExists(attachment_path)
        if not os.path.lexists(source):
            raise OrmAttachmentSourceNotExists(source)
        shutil.move(source, attachment_path)
        return filename, attachment_path

    def move_file_to(self, destination, instance, attr_name, filename=None):
        """ Moves the file from the storage to the specified destination position of the
        file system. File becomes detached from the object instance after.
        @destination            Full path, with filename, where to store a file from the
                                storage;
        @instance               The object instance which holds this file attachment;
        @attr_name              The name of the attribute of the given object instance which
                                represents the file attachment;
        @filename               The filename of the file in the storage. If not set - the
                                method will get filename from the instance's attribute's
                                value (it's representation of the attachment). Usually this
                                is an only right way.
        """
        attachment_path = self.get_absolute_filepath(instance, attr_name, filename)
        if not os.path.lexists(attachment_path):
            raise OrmAttachmentNotExists(attachment_path)
        shutil.move(attachment_path, destination)

    def copy_file_to(self, destination, instance, attr_name, filename=None):
        """ Copies the file from the storage to the specified destination position of the
        file system. File keeps attached after. This operation may take a time to complete
        because file system has to actually copy file from storage.
        @destination            Full path, with filename, where to store a file from the
                                storage;
        @instance               The object instance which holds this file attachment;
        @attr_name              The name of the attribute of the given object instance which
                                represents the file attachment;
        @filename               The filename of the file in the storage. If not set - the
                                method will get filename from the instance's attribute's
                                value (it's representation of the attachment). Usually this
                                is an only right way.
        """
        attachment_path = self.get_absolute_filepath(instance, attr_name, filename)
        if not os.path.lexists(attachment_path):
            raise OrmAttachmentNotExists(attachment_path)
        shutil.copyfile(attachment_path, destination)

    def link_file_to(self, destination, instance, attr_name, filename=None):
        """ Creates a hard link from attached file to the destination one. This operation
        not detachs file from the object instance, but creates a pointer to the same file
        system blocks in the specified position, so any changes in the content of any one
        of those two files will affect the other too.
        Note that this operation requires that both destination file and attachment (storage)
        to be located in the same file system (mounted FS).
        @destination            Full path, with filename, where to store a file from the
                                storage;
        @instance               The object instance which holds this file attachment;
        @attr_name              The name of the attribute of the given object instance which
                                represents the file attachment;
        @filename               The filename of the file in the storage. If not set - the
                                method will get filename from the instance's attribute's
                                value (it's representation of the attachment). Usually this
                                is an only right way.
        """
        attachment_path = self.get_absolute_filepath(instance, attr_name, filename)
        if not os.path.lexists(attachment_path):
            raise OrmAttachmentNotExists(attachment_path)
        os.link(attachment_path, destination)

    def del_file(self, instance, attr_name, filename=None):
        """ Removes the file from the storage.
        @instance               The object instance which holds this file attachment;
        @attr_name              The name of the attribute of the given object instance which
                                represents the file attachment;
        @filename               The filename of the file in the storage. If not set - the
                                method will get filename from the instance's attribute's
                                value (it's representation of the attachment). Usually this
                                is an only right way.
        """
        filepath = self.get_absolute_filepath(instance, attr_name, filename)
        if not os.path.lexists(filepath):
            return
        os.unlink(filepath)

    def rename_file(self, new_filename, instance, attr_name, filename=None):
        attachment_path = self.get_absolute_filepath(instance, attr_name, filename)
        if not os.path.lexists(attachment_path):
            raise OrmAttachmentNotExists(attachment_path)
        new_filename = self.make_filename(instance, attr_name, new_filename)
        new_attachment_path = self.get_absolute_filepath(instance, attr_name, new_filename)
        shutil.move(attachment_path, new_attachment_path)
        return new_filename, new_attachment_path

    def verify_file_existance(self, instance, attr_name, filename=None):
        """ Verify that specified file is really exists in the storage. Useful when object's
        attribute tells that file is attached, but ORM mechanics wants to verify that (because
        database can tell us that file is attached, but it might been deleted). """
        filename = filename or self._get_filename_from_attribute(instance, attr_name)
        if not filename:
            return True
        return os.path.exists(self.get_absolute_filepath(instance, attr_name, filename))

    def get_relative_filepath(self, instance, attr_name, filename=None):
        filename = filename or self._get_filename_from_attribute(instance, attr_name)
        return "/".join((self._compose_rel_path(instance, attr_name), filename))

    def get_absolute_filepath(self, instance, attr_name, filename=None):
        return "/".join((self.base_path, self.get_relative_filepath(instance, attr_name, filename)))


class OrmFileStorage(OrmStorageAbstract):
    """ General files storage. """
    pass


class OrmPictureStorage(OrmStorageAbstract):
    """ Picture storage which implements additional methods to work with images and additional
    logics for pictures' placing. """

    def __init__(self, base_path, **kwargs):
        self.image_format = kwargs.pop('image_format', None)
        self.max_width = kwargs.pop('max_width', None)
        self.max_height = kwargs.pop('max_height', None)
        self.min_width = kwargs.pop('min_width', None)
        self.min_height = kwargs.pop('min_height', None)
        self.quality = kwargs.pop('quality', 100)
        if self.max_width is not None and not isinstance(self.max_width, int):
            raise OrmParameterError("picture storage requires 'max_width' to be type (int) or not set!")
        if self.max_height is not None and not isinstance(self.max_height, int):
            raise OrmParameterError("picture storage requires 'max_height' to be type (int) or not set!")
        if self.min_width is not None and not isinstance(self.min_width, int):
            raise OrmParameterError("picture storage requires 'min_width' to be type (int) or not set!")
        if self.min_height is not None and not isinstance(self.min_height, int):
            raise OrmParameterError("picture storage requires 'min_height' to be type (int) or not set!")
        if not isinstance(self.quality, int) or 0 >= self.quality > 100:
            raise OrmParameterError("picture storage requires 'quality' to be type (int) and be in [1..100]!")
        super(OrmPictureStorage, self).__init__(base_path, **kwargs)

    def _has_dim_limits(self, **kwargs):
        return bool(self.max_height
                    or self.max_width
                    or self.min_height
                    or self.min_width
                    or kwargs.get('max_height', None)
                    or kwargs.get('max_width', None)
                    or kwargs.get('min_height', None)
                    or kwargs.get('min_width', None))

    def _ensure_image_configuration(self, image, **kwargs):
        if not self._has_dim_limits(**kwargs):
            return
        max_width = kwargs.get('max_width', None) or self.max_width
        max_height = kwargs.get('max_height', None) or self.max_height
        min_width = kwargs.get('min_width', None) or self.min_width
        min_height = kwargs.get('min_height', None) or self.min_height
        fit_image(image, max_height=max_height, min_height=min_height, max_width=max_width, min_width=min_width)

    def push_image(self, image, instance, attr_name, filename=None, **kwargs):
        if not filename and not self.uuid_names:
            raise OrmParameterError(
                "picture storage requires filename to be given on 'push_image' when 'uuid_names' is False!"
            )
        filename = self.make_filename(instance, attr_name, filename)
        attachment_dir = self._compose_abs_path(instance, attr_name)
        if not os.path.isdir(attachment_dir):
            os.makedirs(attachment_dir)
        attachment_path = self.get_absolute_filepath(instance, attr_name, filename)
        if os.path.lexists(attachment_path):
            raise OrmAttachmentAlreadyExists(attachment_path)
        image_format = kwargs.get('image_format', None) or self.image_format
        quality = kwargs.get('quality', 100)
        self._ensure_image_configuration(image, **kwargs)
        if image_format is not None:
            image.save(attachment_path, image_format, quality=quality)
        else:
            image.save(attachment_path)
        return filename, attachment_path, image

    def push_image_from(self, source, instance, attr_name, filename=None, **kwargs):
        from PIL import Image
        if not filename and not self.uuid_names:
            raise OrmParameterError(
                "picture storage requires filename to be given on 'push_image' when 'uuid_names' is False!"
            )
        filename = self.make_filename(instance, attr_name, filename)
        attachment_dir = self._compose_abs_path(instance, attr_name)
        if not os.path.isdir(attachment_dir):
            os.makedirs(attachment_dir)
        attachment_path = self.get_absolute_filepath(instance, attr_name, filename)
        if os.path.lexists(attachment_path):
            raise OrmAttachmentAlreadyExists(attachment_path)
        if not os.path.lexists(source):
            raise OrmAttachmentSourceNotExists(source)
        image = Image.open(source)
        image_format = kwargs.get('image_format', None) or self.image_format
        quality = kwargs.get('quality', 100)
        self._ensure_image_configuration(image, **kwargs)
        if image_format is not None:
            image.save(attachment_path, image_format, quality=quality)
        else:
            image.save(attachment_path)
        return filename, attachment_path, image

    def pull_image_to(self, destination, instance, attr_name, filename=None):
        attachment_path = self.get_absolute_filepath(instance, attr_name, filename)
        if not os.path.lexists(attachment_path):
            raise OrmAttachmentNotExists(attachment_path)
        shutil.copyfile(attachment_path, destination)

    def pull_image(self, instance, attr_name, filename=None):
        from PIL import Image
        attachment_path = self.get_absolute_filepath(instance, attr_name, filename)
        if not os.path.lexists(attachment_path):
            raise OrmAttachmentNotExists(attachment_path)
        return Image.open(attachment_path)

