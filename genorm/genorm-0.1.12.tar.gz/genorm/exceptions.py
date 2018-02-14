# -*- coding: utf8 -*-
""" Custom ORM defined exception classes. """


class OrmException(Exception):
    """ Base class for ORM exceptions. """
    pass


class OrmManagementError(OrmException):
    pass


class OrmDefinitionError(OrmException):
    pass


class OrmSessionNotSet(OrmException):
    """ Raises when ORM does not knows which session to use for the object. Programmer must specify
    the session using kwargs argument 'session=' or set default session using manager's method
    'set_session(<session>)'.
    """
    pass


class OrmModelClassMismatch(OrmException):
    """ Mismatch between offered via argument Model and expected one. """
    pass


class OrmAttributeTypeMistake(OrmException):
    """ Mismatch between used by programmer attribute type and expected one. """
    pass


class OrmParameterError(OrmException):
    """ All various parameter errors (type mismatchs, not enough arguments and so on)
    raises this type of exception. """
    pass


class OrmInvalidKey(OrmException):
    pass


class OrmModelDeclarationError(OrmException):
    pass


class OrmRequestError(OrmException):
    pass


class OrmInstanceMustBeWritten(OrmException):
    pass


class OrmInstanceNotFound(OrmException):
    pass


class OrmAttributeIsProtected(OrmException):
    pass


class OrmComparatorValueError(OrmException):
    pass


class OrmValueError(OrmException):
    pass


class OrmTypeError(OrmException):
    pass


class OrmUnacceptableOperation(OrmException):
    """ Raises when trying to do something with the ORM element, which is normal for
    the base type (for example, for list or dict), but is not acceptable for that type's
    ORM custom implementation (for example, for files and pictures lists). """
    pass


class OrmNotDefinedYet(OrmException):
    """ Raises when trying to deal with ORM elements such as attributes while according
    Model definition not finished yet. """
    pass


class OrmLoggingError(OrmException):
    """ Various errors caused in the journaling logics. """
    pass


class OrmRowVersionMismatch(OrmException):
    """ Raises when submitting object been previously changed by other
    process in a time between this object been loaded from the database and
    object updating on the DBMS side, to inform about split brain situation
    avoiding (soft lock mechanism). """
    pass


class OrmProhibittedValueSet(OrmException):
    """ Internal exception, used in the model and engine mechanics to
    inform that mechanics that given value cannot be assigned to. """
    pass


class OrmPasswordIsWeak(OrmException):
    """ Raises when given password is too weak, for (Password)
    attribute class. """
    pass


class OrmAttachmentAlreadyExists(OrmException):
    """ Raises when attachment cannot be saved to the according storage
    due another file with the same name is already exists and attaching
    file cannot be renamed. """
    pass


class OrmAttachmentSourceNotExists(OrmException):
    """ Raises when source file, given in 'path' parameter, is not
    exists at the file system (trying to attach from not existing
    file). """
    pass


class OrmAttachmentNotExists(OrmException):
    """ Raises when the trying to act with attachment - for example,
    save it to the another location of file system, - but attachment
    is not exists (not attached to the attribute). """
    pass


class OrmObjectMustBeWrittenFirst(OrmException):
    """ Raises when trying to deal with object instance which did not
    been written to the database (not INSERTed) before. Some methods,
    data types and functions can only work with already existing
    in the database objects (for example - they can relly on already
    existing ID of object). """
    pass


class OrmValueVerificationError(OrmException):
    pass

