
import time


def _log(debug_logger, msg, args=None):
    if debug_logger:
        if args is not None:
            debug_logger.debug(msg, args)
        else:
            debug_logger.debug(msg)
    elif args:
        print msg % args
    else:
        print msg


def log_timing(start, timed=None, debug_logger=None):
    timing = time.time() - start
    if timed:
        msg = (
            "Timing for %s: %s seconds"
            % (timed, timing))
    else:
        msg = (
            "Timing: %s seconds"
            % timing)
    _log(debug_logger, msg)


def log_new_queries(queries, debug_logger=None):
    from django.db import connection

    new_queries = list(connection.queries[queries:])
    for query in new_queries:
        _log(debug_logger, query['time'])
        _log(debug_logger, "\t%s", query["sql"])
    _log(
        debug_logger,
        "total db calls: %s",
        len(new_queries))
    _log(
        debug_logger,
        "total db time: %s",
        sum([float(q['time']) for q in new_queries]))
