"""
Exceptions that should be raised when failing to store or retrieve an asset via
a backend service.
"""

__all__ = [
    # Exceptions
    'RetrieveError',
    'StoreError'
    ]


class RetrieveError(Exception):
    """
    Raised when a backend services fails to retreve an asset.
    """


class StoreError(Exception):
    """
    Raised when a backend services fails to store an asset.
    """