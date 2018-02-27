if "rook" in __name__:
    # This is caused by not changing sys.path in Rook combined with the way we package the code
    from rook.interfaces.protobuf import rook_pb2
    from rook.interfaces.config import *
    from rook.interfaces.exceptions import *
else:
    from interfaces.protobuf import rook_pb2
    from interfaces.config import *
    from interfaces.exceptions import *
