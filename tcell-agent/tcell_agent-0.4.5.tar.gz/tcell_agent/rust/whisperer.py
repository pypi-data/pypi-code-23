import sys
import json
import os

from ctypes import cdll, c_uint8, c_void_p, c_size_t, c_int, c_char_p, POINTER

from tcell_agent.utils.compat import to_bytes
from tcell_agent.tcell_logger import get_module_logger

version = "0.6.4"
prefix = {"win32": ""}.get(sys.platform, "lib")
extension = {"darwin": ".dylib", "win32": ".dll"}.get(sys.platform, ".so")

try:
    native_lib = cdll.LoadLibrary(os.path.abspath(os.path.join(os.path.dirname(__file__), prefix + "tcellagent-" + version + extension)))

    native_lib.cmdi_parse_sh.argtypes = [c_char_p, c_size_t, POINTER(c_uint8), c_size_t]
    """
        restype [int]: 0+ length of buffer_out answer (parsing was successful)
                       -1 general error
                       -2 buffer_out is not big enough for response
                       -3 command_str is null
    """
    native_lib.cmdi_parse_sh.restype = c_int

    native_lib.appfirewall_policy_init.argtypes = [c_char_p, c_size_t, c_char_p, c_size_t, POINTER(c_uint8), c_size_t]
    """
        restype [int]: 0+ length of buffer_out answer (parsing was successful)
                       -1 general error
                       -2 buffer_out is not big enough for response
                       -3 out is null
    """
    native_lib.appfirewall_policy_init.restype = c_int

    native_lib.appfirewall_policy_apply.argtypes = [c_void_p, c_char_p, c_size_t, POINTER(c_uint8), c_size_t]
    """
        restype [int]: 0+ length of buffer_out answer (parsing was successful)
                       -1 general error
                       -2 buffer_out is not big enough for response
                       -3 out is null
    """
    native_lib.appfirewall_policy_apply.restype = c_int

    native_lib.appfirewall_free.argtypes = [c_void_p]
    native_lib.appfirewall_free.restype = None


except Exception as ex:
    native_lib = None

    get_module_logger(__name__).error("Failed to load common agent library. {e}".format(e=ex))
    get_module_logger(__name__).debug(ex, exc_info=True)


def parse_cmd(cmd):
    if native_lib and cmd and cmd.strip():
        command_bytes = to_bytes(cmd)
        allocated_memory_bytes = 1024 * 8
        buf_type = c_uint8 * allocated_memory_bytes
        response = buf_type()  # allocate memory
        ans = native_lib.cmdi_parse_sh(
            command_bytes, len(command_bytes), response, allocated_memory_bytes)
        if ans >= 0:
            return json.loads("".join([chr(response_byte) for response_byte in response[:ans]]))

    return {}


def init_appfirewall(policy, allow_payloads):
    if native_lib and policy:
        appfirewall_config = {
            "allow_send_payloads": allow_payloads
        }

        policy_bytes = to_bytes(json.dumps(policy))
        config_bytes = to_bytes(json.dumps(appfirewall_config))

        allocated_memory_bytes = 1024 * 8
        buf_type = c_uint8 * allocated_memory_bytes
        response = buf_type()  # allocate memory
        ans = native_lib.appfirewall_policy_init(policy_bytes,
                                                 len(policy_bytes),
                                                 config_bytes,
                                                 len(config_bytes),
                                                 response,
                                                 allocated_memory_bytes)
        if ans >= 0:
            return json.loads("".join([chr(response_byte) for response_byte in response[:ans]]))

    return {}


def apply_appfirewall(appfirewall_ptr, request_response):
    if native_lib and appfirewall_ptr and request_response:
        request_response_bytes = to_bytes(json.dumps(request_response))

        allocated_memory_bytes = 1024 * 8
        buf_type = c_uint8 * allocated_memory_bytes
        response = buf_type()  # allocate memory
        ans = native_lib.appfirewall_policy_apply(appfirewall_ptr,
                                                  request_response_bytes,
                                                  len(request_response_bytes),
                                                  response,
                                                  allocated_memory_bytes)

        if ans >= 0:
            return json.loads("".join([chr(response_byte) for response_byte in response[:ans]]))

    return {}


def free_appfirewall(appfirewall_ptr):
    if native_lib and appfirewall_ptr:
        native_lib.appfirewall_free(appfirewall_ptr)
