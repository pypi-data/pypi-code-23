from future.utils import iteritems

from tcell_agent.appsensor import params
from tcell_agent.utils.json_utils import parse_json


def convert_params(encoding, params_dict, need_to_flatten=True):
    if params_dict is None:
        return []

    flattened_dict = params_dict
    if need_to_flatten:
        flattened_dict = params.flatten_clean(encoding, params_dict)

    flattened_params = []
    for param_name, param_value in iteritems(flattened_dict):
        flattened_params.append({"name": param_name[-1], "value": param_value})

    return flattened_params


def create_request_response(appsensor_meta):
    json_body = parse_json(appsensor_meta.encoding, appsensor_meta.json_body_str)
    if json_body and isinstance(json_body, list):
        json_body = {'body': json_body}

    post_params = convert_params(appsensor_meta.encoding, appsensor_meta.post_dict, False) + \
        convert_params(appsensor_meta.encoding, appsensor_meta.files_dict, False) + \
        convert_params(appsensor_meta.encoding, json_body or {})

    request_response = {
        "method": appsensor_meta.method,
        "status_code": appsensor_meta.response_code,
        "route_id": appsensor_meta.route_id,
        "path": appsensor_meta.path,
        "query_params": convert_params(appsensor_meta.encoding, appsensor_meta.get_dict),
        "post_params": post_params,
        "headers": convert_params(appsensor_meta.encoding, appsensor_meta.headers_dict),
        "cookies": convert_params(appsensor_meta.encoding, appsensor_meta.cookie_dict),
        "path_params": convert_params(appsensor_meta.encoding, appsensor_meta.path_dict),
        "remote_address": appsensor_meta.remote_address,
        "full_uri": appsensor_meta.location,
        "session_id": appsensor_meta.session_id,
        "user_id": appsensor_meta.user_id,
        "user_agent": appsensor_meta.user_agent_str,
        "request_bytes_length": appsensor_meta.request_content_bytes_len,
        "response_bytes_length": appsensor_meta.response_content_bytes_len,
        "sql_exceptions": appsensor_meta.sql_exceptions,
        "database_result_sizes": appsensor_meta.database_result_sizes
    }

    if appsensor_meta.csrf_reason:
        request_response["csrf_exception"] = {"exception_payload": appsensor_meta.csrf_reason}

    return request_response


def create_patches_request(appsensor_meta):
    json_body = parse_json(appsensor_meta.encoding, appsensor_meta.json_body_str)
    post_params = convert_params(appsensor_meta.encoding, appsensor_meta.post_dict, False) + \
        convert_params(appsensor_meta.encoding, appsensor_meta.files_dict, False) + \
        convert_params(appsensor_meta.encoding, json_body or {})

    return {"method": appsensor_meta.method,
            "path": appsensor_meta.path,
            "remote_address": appsensor_meta.remote_address,
            "request_bytes_length": appsensor_meta.request_content_bytes_len,
            "query_params": convert_params(appsensor_meta.encoding, appsensor_meta.get_dict),
            "post_params": post_params,
            "headers": convert_params(appsensor_meta.encoding, appsensor_meta.headers_dict),
            "cookies": convert_params(appsensor_meta.encoding, appsensor_meta.cookie_dict)}
