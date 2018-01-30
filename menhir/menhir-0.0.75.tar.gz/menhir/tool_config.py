"""Functions for working with tool configuration."""
from menhir.utils import is_string, multi, method


def value_array(value_names, info, path, extra_values):
    """Return a list of values for the list of ``value_names``.

    ``value_names`` are first looked up in extra_values.  If not
    specified there, then they are evaluated with ``config_value``.
    """
    def lookup_value(x):
        return lookup_config_value(x, info, path, extra_values)

    return list(map(lookup_value, value_names))


def aliased_value_array(value_names, info, path, extra_values):
    """Return a list of tuples for the list of ``value_names``.

    Each item in ``value_names`` is either a simple config value name,
    or is an ``alias=name`` specification.

    Each returned tuple contains the ``alias`` (defaults to config
    value name) and it's value.

    Value names are first looked up in extra_values.  If not specified
    there, then they are evaluated with ``config_value``.
    """
    def lookup_value(x):
        if '=' in x:
            [n, v] = x.split('=')
        else:
            n = v = x
        return (n, lookup_config_value(v, info, path, extra_values))

    return list(map(lookup_value, value_names))


def lookup_config_value(x, info, path, extra_values):
    value = extra_values.get(x)
    if value is None:
        value = config_value(x, info, path)
    return value % extra_values if is_string(value) else value


@multi
def config_value(name, info, path):
    """Return a configuration value for passing to terraform."""
    return name


@method(config_value, 'project')
def config_value_project(name, info, path):
    return info['project-name']


@method(config_value, 'branch')
def config_value_branch(name, info, path):
    from menhir.project import branch
    return branch()


@method(config_value, 'branch-slug')
def config_value_branch_slug(name, info, path):
    from menhir.project import branch
    from menhir.tool_utils import slugify
    return slugify(branch(), length=22)


@method(config_value, 'sha-mod-1024')
def config_value_sha_mod_1024(name, info, path):
    from menhir.project import sha
    return int(sha(), 16) % 1024


@method(config_value, 'sha')
def config_value_sha(name, info, path):
    from menhir.project import sha
    return sha()


@method(config_value, 'image')
def config_value_image(name, info, path):
    from menhir.project import image
    return image(info, path)
