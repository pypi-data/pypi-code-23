import time
import functools

from datetime import datetime, timedelta


def timing(func):
    """函数计时装饰器

    Args:
        func: 被装饰的函数

    Examples:

        >>> @timing
        ... def t(seconds=2):
        ...     return time.sleep(seconds)
        ...
        >>> ret, duration = t()

    Returns:
        (Any, float): 返回一个二元组 (原函数的返回值, 函数用时)

    """

    @functools.wraps(func)
    def inner(*args, **kwargs):
        start = time.time()
        ret = func(*args, **kwargs)
        return ret, time.time() - start

    return inner


def str_to_date(date_str, fmt='%Y-%m-%d %H:%M'):
    """字符串转 datetime 格式

    常用格式说明：
        %y: 年（需要补零） 00, 01, …, 99
        %Y: 年 2013, 2014, …, 9999
        %m: 月 01, 02, …, 12
        %d: 日 01, 02, …, 31
        %H: 时 00, 01, …, 23
        %M: 分 00, 01, …, 59
        %S: 秒 00, 01, …, 59

    补零的意思指 '1-2-12' -> '01-02-12'
    官方文档虽然说明都要补零，但实测只有 %y 必须补零才能正常转换

        ref: https://docs.python.org/3/library/datetime.html?highlight=strptime#strftime-and-strptime-behavior

    Args:
        date_str (str):
        fmt (str): 时间格式

    Returns:
        datetime:

    Examples:

        >>> str_to_date('2001-02-12 12:01')
        datetime.datetime(2001, 2, 12, 12, 1)


    """
    # if 'y' in fmt:
    #     try:
    #         date = datetime.strptime(date_string, fmt)
    #     except ValueError:
    #         print('The %y need to pad zero.')
    # else:
    #     date = datetime.strptime(date_string, fmt)

    return datetime.strptime(date_str, fmt)


def date_to_time(date, fmt='%Y-%m-%d %H:%M'):
    """datetime 转字符串

    这个函数配合 str_to_date() 可以用来快速修改时间格式，比如
        '21-01-2008' -> '2008-01-21'

    再比如"补零"：
        '2008-1-2' -> '2008-01-02'

    Args:
        date (datetime):
        fmt (str): 时间格式

    Returns:
        str:

    Examples：

        >>> date = str_to_date('2001-1-12 12:2')
        >>> date_to_time(date, '%Y-%m-%d')
        '2001-01-12'

    """
    return datetime.strftime(date, fmt)


def get_timedelta(time_from, time_to, time_delta,
                  need_str=True, fmt_in='%Y-%m-%d', fmt_out='%Y-%m-%d %H:%M'):
    """获取等间隔的时间序列

    在处理缺失数据时，可以配合 pandas 使用

    Args:
        time_from (str or datetime):
        time_to (str or datetime):
        time_delta (int or timedelta): 如果是 int 默认指分钟
        need_str (bool): 是否需要将时间序列转成字符串
        fmt_in: 输入时间的格式
        fmt_out: 输出时间的格式

    Returns:

    """
    if type(time_from) is str:
        time_from = datetime.strptime(time_from, fmt_in)
        time_to = datetime.strptime(time_to, fmt_in)
    if type(time_delta) is int:
        time_delta = timedelta(minutes=time_delta)

    if need_str:
        return ((time_from + time_delta * i).strftime(fmt_out) for i in range(int((time_to - time_from) / time_delta)))
    else:
        return (time_from + time_delta * i for i in range(int((time_to - time_from) / time_delta)))
