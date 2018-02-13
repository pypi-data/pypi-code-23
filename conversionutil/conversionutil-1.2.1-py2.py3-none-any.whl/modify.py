# encoding: utf-8

from logging_helper import LogLines
from future.utils import string_types


def modify_fields(fields,
                  record,
                  modification,
                  add=False,
                  source=None,
                  log_lines=None,
                  log_level=None):
    """
    :param fields: The fields to alter in the record
    :param record: The record dictionary
    :param modification: a function or value
    :param add: if True, adds the field to the record.
                If modification is a function, it must accept a
                default value.
    :param source: A source identifier to add to the log message
    :param log_lines: a LogLines instance to append new lines to
    :param log_level: If log_lines is supplied, this is ignored.
                      If it's None, no logging is done.
                      Otherwise should be a logging level,
                      e.g. INFO, which adds to the logs directly
    :return: None. Note that the record and log_lines objects can
                   be modified by the function
    """
    source = u' of {source} '.format(source=source) if source else u''

    if log_level:
        log_lines = LogLines()

    for field in [fields] if isinstance(fields, string_types) else fields:
        try:
            original = record[field]
            modified = (modification
                        if isinstance(modification, string_types)
                        else modification(original))
            record[field] = modified
            if log_lines:
                log_lines.append(u'Changed "{field}"{source} from '
                                 u'"{original}" to "{modified}"'
                                 .format(field=field,
                                         source=source,
                                         original=original,
                                         modified=modified))
        except KeyError:
            if add:
                modified = (modification
                            if isinstance(modification, string_types)
                            else modification())
                record[field] = modified
                if log_lines:
                    log_lines.append(u'Added "{field}"{source}:"{modified}"'
                                     .format(field=field,
                                             source=source,
                                             modified=modified))
