import traceback

from tcell_agent.agent import TCellAgent, PolicyTypes
from tcell_agent.tcell_logger import get_module_logger


def check_database_errors(request, exc_type, tb):
    try:
        rust_policies = TCellAgent.get_policy(PolicyTypes.RUST)
        if rust_policies and rust_policies.appfirewall_enabled:
            from sqlalchemy.exc import DatabaseError

            if issubclass(exc_type, DatabaseError):
                stack_trace = traceback.format_tb(tb)
                stack_trace.reverse()
                request._appsensor_meta.sql_exceptions.append({
                    "exception_name": exc_type.__name__,
                    "exception_payload": "".join(stack_trace)
                })
    except ImportError:
        pass
    except Exception as exception:
        LOGGER = get_module_logger(__name__)
        LOGGER.debug("Exception during database errors check: {e}".format(e=exception))
        LOGGER.debug(exception, exc_info=True)
