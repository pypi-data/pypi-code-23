"""
This module exposes all primitives under the same ``d3m.primitives`` namespace.

This is achieved using Python entry points. Python packages containing primitives
can register them and expose them under the common namespace by adding an entry
like the following to package's ``setup.py``::

    entry_points = {
        'd3m.primitives': [
            'primitive_namespace.PrimitiveName = my_package.my_module:PrimitiveClassName',
        ],
    },

The example above would expose the ``my_package.my_module.PrimitiveClassName`` primitive under
``d3m.primitives.primitive_namespace.PrimitiveName``.
"""


# We want to keep all local symbols inside a method so that it is easy to clean them.
def populate_primitives():  # type: ignore
    import pkg_resources
    import logging

    # We cannot use a relative import here. It does not work.
    from d3m import index

    logger = logging.getLogger(__name__)

    # Remove the method's symbol we introduced.
    exported_module = globals()
    del exported_module['populate_primitives']

    all_primitives = {}

    for entry_point in pkg_resources.iter_entry_points('d3m.primitives'):
        try:
            try:
                all_primitives[entry_point.name] = entry_point.load(require=True)
            except pkg_resources.ResolutionError as error:
                logger.warning("While loading primitive '%(entry_point_name)s', an error has been detected: %(error)s", {'entry_point_name': entry_point.name, 'error': error})
                logger.warning("Attempting to load primitive '%(entry_point_name)s' without checking requirements.", {'entry_point_name': entry_point.name})
                all_primitives[entry_point.name] = entry_point.load(require=False)
        except Exception:
            logger.exception("Could not load the primitive: %(entry_point_name)s", {'entry_point_name': entry_point.name})

    for primitive_path, primitive in all_primitives.items():
        try:
            index.register_primitive(primitive_path, primitive)
        except Exception:
            logger.exception("Could not register a primitive: %(primitive_path)s", {'primitive_path': primitive_path})

    return tuple(all_primitives.keys())


# So that this module does not throw a misleading error when
# importing something non existent under it:
#
# import d3m.primitives.non_existent
# ImportError: No module named 'd3m.primitives.non_existent'; 'd3m.primitives' is not a package
#
# It should be seen as a package.
__path__ = []  # type: ignore

# To have proper value set for a package.
__package__ = __name__

__all__ = populate_primitives()
