import logging


logger = logging.getLogger(__name__)


def check(condition, message, status=True, category='', i=None, level='warning'):
    """
    Utility function to check a condition and provide (numbered) log messages.

    :param condition: condition to be checked
    :param message: message to be displayed in case of condition=True
    :param status: status of the overall check (useful if several checks are executed after each other)
    :param category: category to be displayed together with message
    :param i: identifier to be displayed together with message
    :param level: logging level of the message displayed in case of condition=True
    :return: new status of the overall check and new identifier
    """

    # Check identifier
    if i is None:
        idx = ''
    else:
        idx = str(i).zfill(2) + ': '

    # Check condition
    if condition:
        full_message = category + idx + message
        if level == 'warning':
            logger.warning(full_message)
        elif level == 'info':
            logger.info(full_message)
        elif level == 'debug':
            logger.debug(full_message)
        else:
            logger.error(full_message)
        status = False

    # Return
    if i is None:
        return status
    else:
        return status, i+1
