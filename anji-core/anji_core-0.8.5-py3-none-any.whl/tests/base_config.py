from uuid import uuid4

import config as base_dict

from anji_core.types import NodeType

__all__ = ['extra_config', 'pytest_plugins']

pytest_plugins = ["anji_core.backends.test"]

extra_config = base_dict.__dict__

extra_config.update({
    'BACKEND': "AnjiTest",
    'ANJI_BOT_TYPE': NodeType.master,
    'ANJI_RETHINK_DB': f'test_{uuid4()}'.replace('-', '_'),
    'BOT_ASYNC': False
})

extra_config.pop('CORE_PLUGINS', None)
