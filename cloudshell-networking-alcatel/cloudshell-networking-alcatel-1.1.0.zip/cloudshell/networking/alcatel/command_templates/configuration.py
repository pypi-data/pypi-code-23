from collections import OrderedDict

from cloudshell.cli.command_template.command_template import CommandTemplate


SHOW_BOF = CommandTemplate('show bof')
SAVE_BOF = CommandTemplate(
    'bof save',
    error_map={
        r'^((?!Completed\.).)*$': Exception('Fail to save BOF'),
    }
)
SHOW_SYS_INFO = CommandTemplate('show system information')

CHANGE_PRIMARY_CONF = CommandTemplate('bof primary-config {path}')
CHANGE_PRIMARY_IMAGE = CommandTemplate('bof primary-image {folder_path}')

REBOOT = CommandTemplate('admin reboot[ upgrade{upgrade}] now')

COPY = CommandTemplate(
    'file copy {src} {dst}',
    action_map={
        'Overwrite destination file:.+\(y/n\)?':
            lambda session, logger: session.send_line('y', logger),
    },
    error_map=OrderedDict([
        (r'There is not enough space', Exception('There is not enough space')),
        (r'^((?!1 file copied).)*$', Exception('Copy failed')),
    ])
)

SAVE_RUNNING_CONFIG = CommandTemplate(
    'admin save {dst}',
    error_map={
        r'^((?!Completed\.).)*$': Exception('Fail to save'),
    }
)

CREATE_FOLDER = CommandTemplate('file md {folder_path}')
