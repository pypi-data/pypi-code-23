import argparse
import json
import inspect
import logging
import sys
import types
import typing
from xmlrpc import client as xmlrpc  # type: ignore

__all__ = ('search', 'discover', 'register_primitive')

logger = logging.getLogger(__name__)


def _traverse_module(current_path: str, module: types.ModuleType) -> typing.Dict[str, type]:
    primitives = {}

    for name in dir(module):
        value = getattr(module, name)
        path = current_path + '.' + name
        if isinstance(value, types.ModuleType):
            primitives.update(_traverse_module(path, value))
        # Primitives are classes.
        elif inspect.isclass(value):
            primitives[path] = value

    return primitives


def search(*, primitive_path_prefix: str = None) -> typing.Dict[str, type]:
    """
    Returns a map from primitive path (Python path inside the D3M namespace) to a primitive class,
    for all known (discoverable through entry points) primitives, or limited by the
    ``primitive_path_prefix`` search argument.

    Parameters
    ----------
    primitive_path_prefix : str
        Optionally limit returned primitives only to those whose path start with ``primitive_name_prefix``.

    Returns
    -------
    Dict[str, type]
        A map from primitive path to its class.
    """

    # We import it inside the function because this import is potentially expensive.
    from . import primitives

    all_primitives = _traverse_module(primitives.__name__, primitives)

    if primitive_path_prefix is None:
        return all_primitives
    else:
        return {primitive_path: primitive for primitive_path, primitive in all_primitives.items() if primitive_path.startswith(primitive_path_prefix)}


def discover(index: str = 'https://pypi.python.org/pypi') -> typing.Tuple[str, ...]:
    """
    Returns package names from PyPi which provide D3M primitives.

    This is determined by them having a ``d3m_primitive`` among package keywords.

    Parameters
    ----------
    index : str
        Base URL of Python Package Index to use.

    Returns
    -------
    Tuple[str]
        A list of package names.
    """

    client = xmlrpc.ServerProxy(index)
    hits = client.search({'keywords': 'd3m_primitive'})
    return tuple(sorted(list({package['name'] for package in hits})))


def register_primitive(primitive_path_suffix: str, primitive: type) -> None:
    """
    Registers a primitive under ``d3m.primitives`` namespace.

    If ``primitive_path_suffix`` is equal to ``foo.bar.Baz``, the primitive will be registered
    under ``d3m.primitives.foo.bar.Baz``.

    Parameters
    ----------
    primitive_path_suffix : str
        A primitive path suffix to register a primitive under.
    primitive : type
        A primitive class to register.
    """

    if not primitive_path_suffix:
        raise ValueError("Path under which to register a primitive is required.")

    if not inspect.isclass(primitive):
        raise TypeError("Primitive to register has to be a class.")

    if '.' in primitive_path_suffix:
        modules_path, name = primitive_path_suffix.rsplit('.', 1)
        modules = modules_path.split('.')
    else:
        name = primitive_path_suffix
        modules = []

    if 'd3m.primitives' not in sys.modules:
        import d3m.primitives

    # Create any modules which do not yet exist.
    current_path = 'd3m.primitives'
    for module in modules:
        module_path = current_path + '.' + module

        if module_path not in sys.modules:
            # Because "module_path not in sys.modules" we know that it is not a module which would
            # exist in sys.modules[current_path], but something else, which we do not want to clobber.
            if hasattr(sys.modules[current_path], module):
                raise ValueError("{module}.{name} is already defined.".format(module=current_path, name=module))

            module_type = types.ModuleType(module_path)

            # To make sure there is no misleading error when importing something non existent under it.
            # Se bellow for details.
            module_type.__path__ = []  # type: ignore

            # To have proper value set for a package.
            module_type.__package__ = module_path

            sys.modules[module_path] = module_type
            setattr(sys.modules[current_path], module, module_type)

        current_path = module_path

    if hasattr(sys.modules[current_path], name):
        # Registering twice the same primitive is a noop.
        if getattr(sys.modules[current_path], name) is primitive:
            return

        raise ValueError("{module}.{name} is already defined.".format(module=current_path, name=name))

    setattr(sys.modules[current_path], name, primitive)


def main() -> None:
    logging.basicConfig()

    parser = argparse.ArgumentParser(description="Explore D3M primitives.")
    subparsers = parser.add_subparsers(dest='command', title='commands')
    subparsers.required = True  # type: ignore

    search_parser = subparsers.add_parser(
        'search', help="search locally available primitives",
        description="Searches locally available primitives. Lists registered Python paths to primitive classes for primitives installed on the system.",
    )
    discover_parser = subparsers.add_parser(
        'discover', help="discover primitives available on PyPi",
        description="Discovers primitives available on PyPi. Lists package names containing D3M primitives on PyPi.",
    )
    describe_parser = subparsers.add_parser(
        'describe', help="generate a JSON description of a primitive",
        description="Generates a JSON description of a primitive.",
    )

    search_parser.add_argument(
        '-p', '--prefix', action='store',
        help="primitive path prefix to limit search results to"
    )

    discover_parser.add_argument(
        '-i', '--index', default='https://pypi.python.org/pypi', action='store',
        help="base URL of Python Package Index to use, default https://pypi.python.org/pypi"
    )

    describe_parser.add_argument(
        'primitive', action='store',
        help="primitive path identifying a primitive to describe"
    )
    describe_parser.add_argument(
        '-i', '--indent', type=int, default=4, action='store',
        help="indent JSON by this much, 0 disables indentation, default 4"
    )

    arguments = parser.parse_args()

    if arguments.command == 'search':
        for primitive_name in search(primitive_path_prefix=arguments.prefix).keys():
            print(primitive_name)

    elif arguments.command == 'discover':
        for package_name in discover(index=arguments.index):
            print(package_name)

    elif arguments.command == 'describe':
        all_primitives = search(primitive_path_prefix=arguments.primitive)

        primitive = all_primitives.get(arguments.primitive)
        if primitive is None:
            logger.error("Primitive not found: %(primitive_name)s", {'primitive_name': arguments.primitive})
            sys.exit(1)

        json.dump(primitive.metadata.to_json(), sys.stdout, indent=(arguments.indent or None))  # type: ignore
        sys.stdout.write('\n')

    else:
        assert False, arguments.command


if __name__ == '__main__':
    main()
