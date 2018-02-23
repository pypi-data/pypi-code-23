# encoding: utf-8

import os
import codecs
import logging_helper
from ruamel.yaml import YAML

logging = logging_helper.setup_logging()


def get_default_yaml_instance(**kwargs):
    # Setup YAML instance
    yaml = YAML(**kwargs)
    yaml.default_flow_style = False
    yaml.explicit_start = True
    yaml.explicit_end = True

    return yaml


def write_yaml_to_file(content,
                       output_dir,
                       filename,
                       backup_dir=None,
                       file_ext=u'yaml',
                       yaml=None):

    """ Write some data into a file

    :param content:     (str)    Variable containing some data to be written into the file
    :param output_dir:  (str)    Directory the file is to be written to
    :param backup_dir:  (str)    Directory an existing file of the same name will be moved to (overwrites)
    :param filename:    (str)    new files filename
    :param file_ext:    (str)    new files extension
    :param yaml:        (obj)    A ruamel.yaml.YAML() instance configured to your taste.
                                 If none provided the following will be used:
                                    yaml = YAML()
                                    yaml.default_flow_style = False
                                    yaml.explicit_start = True
                                    yaml.explicit_end = True

    :return:            tuple:  (new file path, backup file path)
    """

    if yaml is None:
        yaml = get_default_yaml_instance()

    out_file = u'{feed}.{ext}'.format(feed=filename,
                                      ext=file_ext)

    file_path = u'{p}{s}{f}'.format(p=output_dir,
                                    s=os.sep,
                                    f=out_file)

    backup_path = u''

    if backup_dir:

        # Move existing file to backup directory
        if os.path.isfile(file_path):

            backup_path = u'{p}{s}{f}'.format(p=backup_dir,
                                              s=os.sep,
                                              f=out_file)

            if os.path.isfile(backup_path):
                os.remove(backup_path)

            os.rename(file_path,
                      backup_path)

    else:
        if os.path.isfile(file_path):
            os.remove(file_path)

    # Write out new file to output directory
    with codecs.open(file_path, mode=u'wb', encoding=u'utf-8') as json_file:
        yaml.dump(content,
                  json_file)

    return file_path, backup_path
