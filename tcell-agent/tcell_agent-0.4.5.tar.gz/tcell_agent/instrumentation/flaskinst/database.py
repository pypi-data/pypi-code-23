from tcell_agent.agent import TCellAgent, PolicyTypes
from tcell_agent.tcell_logger import get_module_logger


def check_database_errors(request, exc_type, stack_trace):
    try:
        appsensor_policy = TCellAgent.get_policy(PolicyTypes.APPSENSOR)
        if appsensor_policy:
            from sqlalchemy.exc import DatabaseError
            if issubclass(exc_type, DatabaseError):
                appsensor_policy.sql_exception_detected(request._appsensor_meta, exc_type.__name__, stack_trace)
    except ImportError:
        pass
    except Exception as exception:
        LOGGER = get_module_logger(__name__)
        LOGGER.debug("Exception during database errors check: {e}".format(e=exception))
        LOGGER.debug(exception, exc_info=True)
