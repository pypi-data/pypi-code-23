"""
Collection of mtbparser exceptions.
"""
class MtbUnknownFileType(Exception):
    """Raise, if the MTB file type could not be determined"""

class MtbIncompleteArchive(Exception):
    """Raise, if the MTB archive is missing files"""

class MtbUnknownBarcode(Exception):
    """Raise, if not all archive members contain the same barcode."""

class NoReferenceIdFound(Exception):
    """Raise, if the a flexible data set instance has no reference id."""

class ParseConfigFileException(Exception):
    """Raise, when the parsing of the config file fails"""