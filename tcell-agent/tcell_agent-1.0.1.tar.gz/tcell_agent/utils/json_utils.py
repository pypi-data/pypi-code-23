import json

from tcell_agent.sanitize.sanitize_utils import ensure_str_or_unicode

from tcell_agent.tcell_logger import get_module_logger


def parse_json(encoding, json_str):
    if not json_str:
        return None

    if isinstance(json_str, dict) or isinstance(json_str, list):  # Already a dict
        return json_str

    try:
        return json.loads(ensure_str_or_unicode(encoding, json_str))
    except Exception as e:
        LOGGER = get_module_logger(__name__)
        LOGGER.error("Error decoding json: {e}".format(e=e))
        LOGGER.debug(e, exc_info=True)
        return None
