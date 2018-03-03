import sys
import json
import os

from ctypes import cdll, c_uint8, c_void_p, c_size_t, c_int, c_char_p, POINTER

from tcell_agent.config.configuration import CONFIGURATION
from tcell_agent.rust.request_response import create_request_response, create_patches_request
from tcell_agent.tcell_logger import get_module_logger
from tcell_agent.utils.compat import to_bytes

version = "0.11.1"
prefix = {"win32": ""}.get(sys.platform, "lib")
extension = {"darwin": ".dylib", "win32": ".dll"}.get(sys.platform, ".so")

try:
    native_lib = cdll.LoadLibrary(os.path.abspath(os.path.join(os.path.dirname(__file__), prefix + "tcellagent-" + version + extension)))

    native_lib.create_agent.argtypes = [c_char_p, c_size_t, POINTER(c_uint8), c_size_t]
    """
        restype [int]: 0+ length of buffer_out answer
                       -1 general error
                       -2 buffer_out is not big enough for response
                       -3 buffer_out is null
    """
    native_lib.create_agent.restype = c_int

    native_lib.update_policies.argtypes = [c_void_p, c_char_p, c_size_t, POINTER(c_uint8), c_size_t]
    """
        restype [int]: 0+ length of buffer_out answer
                       -1 general error
                       -2 buffer_out is not big enough for response
                       -3 buffer_out is null
    """
    native_lib.update_policies.restype = c_int

    native_lib.appfirewall_apply.argtypes = [c_void_p, c_char_p, c_size_t, POINTER(c_uint8), c_size_t]
    """
        restype [int]: 0+ length of buffer_out answer
                       -1 general error
                       -2 buffer_out is not big enough for response
                       -3 buffer_out is null
    """
    native_lib.appfirewall_apply.restype = c_int

    native_lib.patches_apply.argtypes = [c_void_p, c_char_p, c_size_t, POINTER(c_uint8), c_size_t]
    """
        restype [int]: 0+ length of buffer_out answer
                       -1 general error
                       -2 buffer_out is not big enough for response
                       -3 buffer_out is null
    """
    native_lib.patches_apply.restype = c_int

    native_lib.cmdi_apply.argtypes = [c_void_p, c_char_p, c_size_t, POINTER(c_uint8), c_size_t]
    """
        restype [int]: 0+ length of buffer_out answer
                       -1 general error
                       -2 buffer_out is not big enough for response
                       -3 buffer_out is null
    """
    native_lib.cmdi_apply.restype = c_int

except Exception as ex:
    native_lib = None

    get_module_logger(__name__).error("Failed to load common agent library. {e}".format(e=ex))
    get_module_logger(__name__).debug(ex, exc_info=True)


def get_library_response(function_called, response, response_len):
    if response_len >= 0:
        try:
            return json.loads("".join([chr(response_byte)
                                       for response_byte in response[:response_len]]))
        except ValueError:
            get_module_logger(__name__).warn("Could not decode json response from" +
                                             "`{}` in native library.".format(function_called))

    else:
        get_module_logger(__name__).warn(
            "Error response from `{}` in native library: {}".format(function_called,
                                                                    response_len))

    return {}


def create_agent():
    if native_lib:
        agent_config = {
            "appfirewall": {
                "enable_body_xxe_inspection": False,
                "enable_body_json_inspection": False,
                "allow_send_payloads": CONFIGURATION.allow_payloads,
                "allow_log_payloads": True
            }
        }
        config_bytes = to_bytes(json.dumps(agent_config))

        allocated_memory_bytes = 1024 * 8
        buf_type = c_uint8 * allocated_memory_bytes
        response = buf_type()  # allocate memory
        response_len = native_lib.create_agent(
            config_bytes, len(config_bytes), response, allocated_memory_bytes
        )
        return get_library_response("create_agent", response, response_len)

    return {}


def update_policies(agent_ptr, policy):
    if native_lib and policy:
        policy_bytes = to_bytes(json.dumps(policy))

        allocated_memory_bytes = 1024 * 8
        buf_type = c_uint8 * allocated_memory_bytes
        response = buf_type()  # allocate memory
        response_len = native_lib.update_policies(
            agent_ptr, policy_bytes, len(policy_bytes), response, allocated_memory_bytes
        )
        return get_library_response("update_policies", response, response_len)

    return {}


def apply_appfirewall(agent_ptr, appsensor_meta):
    if native_lib and agent_ptr and appsensor_meta:
        request_response = create_request_response(appsensor_meta=appsensor_meta)
        request_response_bytes = to_bytes(json.dumps(request_response))

        allocated_memory_bytes = 1024 * 8
        buf_type = c_uint8 * allocated_memory_bytes
        response = buf_type()  # allocate memory
        response_len = native_lib.appfirewall_apply(agent_ptr,
                                                    request_response_bytes,
                                                    len(request_response_bytes),
                                                    response,
                                                    allocated_memory_bytes)

        return get_library_response("apply_appfirewall", response, response_len)

    return {}


def apply_patches(agent_ptr, appsensor_meta):
    if native_lib and agent_ptr and appsensor_meta:
        patches_request = create_patches_request(appsensor_meta=appsensor_meta)
        patches_request_bytes = to_bytes(json.dumps(patches_request))

        allocated_memory_bytes = 1024 * 8
        buf_type = c_uint8 * allocated_memory_bytes
        response = buf_type()  # allocate memory
        response_len = native_lib.patches_apply(agent_ptr,
                                                patches_request_bytes,
                                                len(patches_request_bytes),
                                                response,
                                                allocated_memory_bytes)

        return get_library_response("apply_patches", response, response_len)

    return {}


def apply_cmdi(agent_ptr, cmd):
    if native_lib and agent_ptr and cmd and cmd.strip():
        command_bytes = to_bytes(cmd)

        allocated_memory_bytes = 1024 * 8
        buf_type = c_uint8 * allocated_memory_bytes
        response = buf_type()  # allocate memory
        response_len = native_lib.cmdi_apply(agent_ptr,
                                             command_bytes,
                                             len(command_bytes),
                                             response,
                                             allocated_memory_bytes)

        return get_library_response("apply_cmdi", response, response_len)

    return {}
