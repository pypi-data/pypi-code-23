from .keras_callback import KerasCallback
from .pycaffe_callback import PyCaffeCallback
from .pytorch_project import PyTorchProject
from .tensorflow_callback import TensorFlowCallback
from .tensorflow_project import TensorFlowProject

global_root_logger_sniffer = None


def set_global_root_logger_sniffer(global_root_logger_sniffer_):
    global global_root_logger_sniffer

    global_root_logger_sniffer = global_root_logger_sniffer_


def get_global_root_logger_sniffer():
    return global_root_logger_sniffer


__all__ = [
    'KerasCallback', 'TensorFlowCallback', 'PyTorchProject', 'PyCaffeCallback', 'TensorFlowProject',
    'set_global_root_logger_sniffer']
