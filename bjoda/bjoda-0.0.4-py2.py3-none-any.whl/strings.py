"""
strings and exit code related information
"""
EXIT_CODES = {
    1: {
        'id': 'GENERR',
        'message': 'General Error'
    },
    2: {
        'id': 'INV_USE',
        'message': 'Misuse of shell builtins'
    },
    124: {
        'id': 'TIMEOUT',
        'message': 'Command Timed Out'
    },
    126: {
        'id': 'NOT_EXE',
        'message': 'Command not Executable'
    },
    128: {
        'id': 'INV_EXIT',
        'message': 'Invalid Exit Argument'
    },
    130: {
        'id': 'CTRL_C',
        'message': 'Control-C Pressed'
    },
    134: {
        'id': 'ABORT',
        'message': 'Command Aborted'
    },
    137: {
        'id': 'TIMEOUT',
        'message': 'Command Timed Out'
    },
    139: {
        'id': 'SEGFAULT',
        'message': 'Segmentation Fault'
    }
}

EXIT_STRINGS = {
    key: '[{}][{}] {}'.format(
        key,
        EXIT_CODES[key]['id'],
        EXIT_CODES[key]['message']
    ) for key in EXIT_CODES
}
