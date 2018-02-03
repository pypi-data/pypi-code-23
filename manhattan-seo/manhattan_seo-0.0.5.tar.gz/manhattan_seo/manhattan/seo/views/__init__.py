from collections import namedtuple

from .update import update_chains

__all__ = ['generic']


# We name space generic views using a named tuple to provide a slightly nicer
# way to access them, e.g:
#
#     from manhattan.seo.views import generic
#
#     view = generic.add
#
# And to make it easy to iterate through the list of generic views to make
# changes, e.g:
#
#     def authenticate(state):
#         """A custom authenticator for my site"""
#
#         ...
#
#     for view in generic:
#         view.set_link(authenticate)

# Define the named tuple (preventing the list of generic views being altered)
Generic = namedtuple(
    'Generic',
    [
        'update'
    ]
)

# Create an instance of Generic containing all the generic views
generic = Generic(
    update=update_chains
)
