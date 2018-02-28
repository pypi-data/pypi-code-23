#!/usr/bin/python

def get_error_message(sys_exc_info):
    """
    Gets single line error message from last error in except: block

    Args:
        sys_exc_info: result from call to sys.exc_info()

    Returns:
        A string with the error traceback message, with ' | ' instead of '\n'
    """
    import traceback
    err_type, err_val, sys_tb_object = sys_exc_info
    error_message = [str(err_type), err_val.__doc__]
    for i, tbtext in enumerate(traceback.format_tb(sys_tb_object)):
        toret = tbtext.split('\n')
        error_message.append(str(i))
        error_message.append(toret[0].strip())
        error_message.append(toret[1].strip())
    return ' | '.join(error_message)
