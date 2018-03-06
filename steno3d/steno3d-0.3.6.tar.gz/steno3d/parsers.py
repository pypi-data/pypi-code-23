"""There are parser modules available for Steno3D to read certain file
types. When a parser module is imported, the available parsers appear
inside `steno3d.parsers`.
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from os.path import expanduser as _expanduser
from os.path import isfile as _isfile
from os.path import realpath as _realpath

import properties
from six import with_metaclass as _with_metaclass
from six import string_types as _string_types

from .project import Project as _Project
from .props import HasSteno3DProps


class _ParserMetaClass(HasSteno3DProps.__class__):
    """metaclass ParserMetaclass

    Metaclass to ensure Parser classes fit the required format and
    get added to the steno3d.parsers namespace
    """

    def __new__(mcs, name, bases, attrs):
        if name != 'BaseParser':
            assert 'extensions' in attrs, \
                "You must give the `extensions` that are supported by the " \
                "{name} parser, e.g. ('obj',)".format(name=name)
            exts = attrs['extensions']
            assert isinstance(exts, tuple) and len(exts) > 0, \
                'The `extensions` in the {name} parser must be a tuple of ' \
                'supported extensions'.format(name=name)
            for ext in exts:
                assert isinstance(ext, _string_types), \
                    'Extensions in the {name} parser must be ' \
                    'strings'.format(name=name)
            assert '__init__' not in attrs, \
                "The BaseParser __init__ function takes the file_name and " \
                "any additional keyword input. Please perform other " \
                "initialization tasks for the {name} parser in " \
                "_initialize()".format(name=name)
            assert 'parse' in attrs and callable(attrs['parse']), \
                "Parser class {name} must contain a parse() method"
        new_class = super(_ParserMetaClass, mcs).__new__(
            mcs, name, bases, attrs
        )
        globals()[name] = new_class
        return new_class


class BaseParser(_with_metaclass(_ParserMetaClass,
                                 HasSteno3DProps)):
    """Base class for Steno3D parser objects

    BaseParser itself cannot be instantiated. Please use the specific
    parser corresponding to your file type or `AllParsers` instead.
    For more information about parsers, see
    https://python.steno3d.com/en/latest/content/parser.html
    """

    extensions = (None,)
    file_name = properties.String(
        doc='The file to parse'
    )
    project = properties.Instance(
        doc='The project to parse file_name into',
        instance_class=_Project,
    )

    def __init__(self, file_name):
        super(BaseParser, self).__init__()
        if self.extensions[0] is None:
            raise ParseError(
                '\nPlease use the specific parser corresponding to your '
                'file type or \n`AllParsers`, not `BaseParser`. For more '
                'information about parsers, see\n'
                'https://python.steno3d.com/en/latest/content/parsers.html'
            )
        self.file_name = self._validate_file(file_name)
        self._initialize()

    def _validate_file(self, file_name):
        """function _validate_file

        Input:
            file_name - The file to be validated

        Output:
            validated file_name

        _validate_file verifies the file exists and the extension matches
        the parser extension(s) before proceeding. This hook can be
        overwritten to perform different file checks or remove the checks
        entirely as long as it returns the file_name.
        """
        if not isinstance(file_name, _string_types):
            raise ParseError(
                '{}: file_name must be a string'.format(file_name)
            )
        file_name = _realpath(_expanduser(file_name))
        if not _isfile(file_name):
            raise ParseError('{}: File not found.'.format(file_name))
        fnsplit = file_name.split('.')
        if (
                len(fnsplit) < 2 or
                fnsplit[-1].upper() not in [ext.upper() for ext
                                            in self.extensions]
        ):
            raise ParseError('{name}: Unsupported extension. Supported '
                             'extensions are {exts}'.format(
                                 name=file_name,
                                 exts='(' + ', '.join(self.extensions) + ')'
                             ))
        return file_name

    def _initialize(self):
        """function _initialize

        _initialize is a hook that is called during parser __init__
        after _validate_file. It can be overwritten to perform any
        additional startup tasks
        """

    def parse(self, project=None, **kwargs):
        """function parse

        Parses the file provided at parser instantiation into a
        Steno3D project.

        Optional input:
            project - Preexisting project to add resources to. If not
                      provided, a new project will be created.

        Output:
            tuple of Steno3D project(s) parsed from file_name
        """
        raise NotImplementedError()


class _AllParserMetaClass(HasSteno3DProps.__class__):
    """metaclass AllParserMetaClass

    Metaclass to ensure AllParser classes fit the requried format and
    get added to the steno3d.parsers namespace
    """

    def __new__(mcs, name, bases, attrs):
        if name != 'AllParsers':
            assert 'extensions' in attrs, \
                "{name} must contain a dictionary of extensions and " \
                "parsers named `extensions`".format(name=name)
            assert isinstance(attrs['extensions'], dict), \
                "{name} extensions must be a dictionary of extensions and " \
                "supporting parser".format(name=name)
            for ext in attrs['extensions']:
                assert isinstance(ext, _string_types), \
                    'Extensions in {name} must be strings'.format(name=name)
                assert issubclass(type(attrs['extensions'][ext]),
                                  _ParserMetaClass), \
                    'Extensions in {name} must direct to a ' \
                    'Parser class'.format(name=name)
        new_class = super(_AllParserMetaClass, mcs).__new__(
            mcs, name, bases, attrs
        )
        globals()[name] = new_class
        return new_class


class AllParsers(_with_metaclass(_AllParserMetaClass,
                                 HasSteno3DProps)):
    """class AllParsers

    Steno3D parser class that selects the appropriate parser for a file
    based on the file's extension. File type must have a corresponding
    parser imported.
    """

    def __new__(cls, file_name, **kwargs):
        if getattr(cls, 'extensions', None) is None:
            cls.extensions = dict()
            parser_keys = [
                k for k in globals()
                if (k != 'BaseParser' and
                    issubclass(type(globals()[k]), _ParserMetaClass))
            ]
            if len(parser_keys) == 0:
                raise ParseError(
                    '\nNo parsers imported! For more information on how to '
                    'use parsers, please see\n'
                    'https://python.steno3d.com/en/latest/content/parsers.html'
                )
            for k in parser_keys:
                for ext in globals()[k].extensions:
                    if ext not in cls.extensions:
                        cls.extensions[ext] = globals()[k]
                    elif issubclass(type(cls.extensions[ext]),
                                    _ParserMetaClass):
                        cls.extensions[ext] = (cls.extensions[ext].__name__ +
                                               ', ' + globals()[k].__name__)
                    else:
                        cls.extensions[ext] = (cls.extensions[ext] +
                                               ', ' + globals()[k].__name__)
        fnsplit = file_name.split('.')
        for ext in cls.extensions:
            if len(fnsplit) > 1 and fnsplit[-1].upper() == ext.upper():
                if issubclass(type(cls.extensions[ext]), _ParserMetaClass):
                    return cls.extensions[ext](file_name, **kwargs)

                raise ParseError(
                    '{ext}: file type supported by more than one parser. '
                    'Please specify one of ({parsers})'.format(
                        ext=ext,
                        parsers=cls.extensions[ext]
                    )
                )

        raise ParseError(
            '{bad}: unsupported file extensions. Must be in ({ok})'.format(
                bad=fnsplit[-1] if len(fnsplit) > 1 else file_name,
                ok=', '.join(list(cls.extensions))
            )
        )


class ParseError(IOError):
    """class ParseError

    Custom exception to raise for errors during file parsing
    """

try:
    del absolute_import, division, print_function, unicode_literals
except NameError:
    # Error cleaning namespace
    pass
