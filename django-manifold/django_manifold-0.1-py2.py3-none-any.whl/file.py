from django.conf import settings
import thriftpy


# The Thrift file as an in-memory Python module
thrift_module = thriftpy.load(
    settings.THRIFT["FILE"],
    module_name=settings.THRIFT["FILE"].replace('.', '_')
)

# Specifically the Thrift Service defined in the Thrift file
thrift_service = getattr(thrift_module, settings.THRIFT["SERVICE"])


def new(ttype, *args, **kwargs):
    """Shortcut to create thrift structs
    :param ttype: Thrift struct name as a string
    :param args: Args to pass to constructor
    :param kwargs: kwargs to pass to constructor
    :return: instantiated object of `ttype`
    """
    return getattr(thrift_module, ttype)(*args, **kwargs)
