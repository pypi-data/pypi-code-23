import patches


HAVE_ZCATALOG = False
try:
    import Products.ZCatalog
    HAVE_ZCATALOG = True
    import catalog
except ImportError:
    HAVE_ZCATALOG = False


def initialize(context):
    """Initializer called when used as a Zope 2 product."""


__all__ = (
    'patches',
    'catalog',
    'Products',
)
