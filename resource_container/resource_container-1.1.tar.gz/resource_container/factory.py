import os
import yaml
from general_tools.file_utils import write_file
from .ResourceContainer import RC

current_version = '0.2'


def load(path, strict=True):
    """
    Loads a resource container from the disk.
    When strict mode is enabled this will reject with an error if validation fails.

    :param path: the RC directory.
    :param strict: default is true. When false the RC will not be validated.
    :return: the loaded resource container
    """
    path = os.path.expanduser(path)
    rc = RC(path)

    if strict is False:
        return rc
    else:
        if rc.manifest is None:
            raise Exception('Not a resource container. Missing manifest.yaml')

        if rc.conforms_to is None:
            raise Exception('Not a resource container. Missing required key: dublin_core.conformsto')

        # TODO: differentiate between outdated and newer resource containers
        if rc.conforms_to != current_version:
            raise Exception('Unsupported resource container version. Found ' + rc.conforms_to + ' but expected ' + current_version)

        return rc


def create(path, manifest):
    """
    Creates a new resource container.
    Throws an error if the container already exists.

    :param path: the directory of the new RC
    :param manifest:  the manifest that will be injected into the RC
    :return: the newly created resource contianer
    """
    path = os.path.expanduser(path)
    if os.path.isdir(path):
        raise Exception('Resource container already exists')

    defaults = {
        'dublin_core': {
            'type': '',
            'conformsto': 'rc' + current_version,
            'format': '',
            'identifier': '',
            'title': '',
            'subject': '',
            'description': '',
            'language': {
                'identifier': '',
                'title': '',
                'direction': ''
            },
            'source': [],
            'rights': '',
            'creator': '',
            'contributor': [],
            'relation': [],
            'publisher': '',
            'issued': '',
            'modified': '',
            'version': ''
        },
        'checking': {
            'checking_entity': [],
            'checking_level': ''
        },
        'projects': []
    }

    if 'type' not in manifest['dublin_core']:
        raise Exception('Missing required key: dublin_core.type')

    if 'format' not in manifest['dublin_core']:
        raise Exception('Missing required key: dublin_core.format')

    if 'identifier' not in manifest['dublin_core']:
        raise Exception('Missing required key: dublin_core.identifier')

    if 'language' not in manifest['dublin_core']:
        raise Exception('Missing required key: dublin_core.language')

    if 'rights' not in manifest['dublin_core']:
        raise Exception('Missing required key: dublin_core.rights')

    if 'checking' not in manifest:
        manifest['checking'] = {}

    if 'projects' not in manifest:
        manifest['projects'] = []

    defaults['dublin_core'].update(manifest['dublin_core'])
    defaults['checking'].update(manifest['checking'])
    opts = {
        'dublin_core': defaults['dublin_core'],
        'checking': defaults['checking'],
        'projects': defaults['projects'] + manifest['projects']
    }

    if not os.path.isdir(path):
        os.makedirs(path)

    write_file(os.path.join(path, 'manifest.yaml'), yaml.dump(opts, default_flow_style=False))

    rc = load(path)
    return rc
