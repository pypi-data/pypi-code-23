import re


def parse_arg_names(regex):
    """Parses the names of the arguments.

    Parameters
    ----------
    regex : string
        The regular expression to parse the arguments from.

    Returns
    -------
    args : list of string
        The arguments found.
    """
    pattern = r'\(\?P<(.+?)>'

    args = re.findall(pattern, regex)
    args = [arg.replace('_', '-') for arg in args]
    return args


def parse(message, regex):
    """Parses the message into its arguments.

    Parameters
    ----------
    message : string
        The message to parse.
    regex : string
        The regular expression to parse it with.

    Returns
    -------
    args : { argname: argval(string) }
    """
    res = re.search(regex, message)
    if res is None:
        return False

    res = res.groupdict()
    args = {}
    for arg in res:
        args[arg.replace('_', '-')] = res[arg]

    return args
