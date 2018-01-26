# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: tensorflow/core/framework/graph_transfer_info.proto

import sys
_b=sys.version_info[0]<3 and (lambda x:x) or (lambda x:x.encode('latin1'))
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
from google.protobuf import descriptor_pb2
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()


from tensorflow.core.framework import types_pb2 as tensorflow_dot_core_dot_framework_dot_types__pb2


DESCRIPTOR = _descriptor.FileDescriptor(
  name='tensorflow/core/framework/graph_transfer_info.proto',
  package='tensorflow',
  syntax='proto3',
  serialized_pb=_b('\n3tensorflow/core/framework/graph_transfer_info.proto\x12\ntensorflow\x1a%tensorflow/core/framework/types.proto\"\xab\t\n\x11GraphTransferInfo\x12\x39\n\tnode_info\x18\x01 \x03(\x0b\x32&.tensorflow.GraphTransferInfo.NodeInfo\x12\x44\n\x0f\x63onst_node_info\x18\x02 \x03(\x0b\x32+.tensorflow.GraphTransferInfo.ConstNodeInfo\x12\x44\n\x0fnode_input_info\x18\x03 \x03(\x0b\x32+.tensorflow.GraphTransferInfo.NodeInputInfo\x12\x46\n\x10node_output_info\x18\x04 \x03(\x0b\x32,.tensorflow.GraphTransferInfo.NodeOutputInfo\x12O\n\x15graph_input_node_info\x18\x05 \x03(\x0b\x32\x30.tensorflow.GraphTransferInfo.GraphInputNodeInfo\x12Q\n\x16graph_output_node_info\x18\x06 \x03(\x0b\x32\x31.tensorflow.GraphTransferInfo.GraphOutputNodeInfo\x12>\n\x0b\x64\x65stination\x18\x07 \x01(\x0e\x32).tensorflow.GraphTransferInfo.Destination\x1a\x31\n\tNodeInput\x12\x0f\n\x07node_id\x18\x01 \x01(\x05\x12\x13\n\x0boutput_port\x18\x02 \x01(\x05\x1a\x8e\x01\n\x08NodeInfo\x12\x0c\n\x04name\x18\x01 \x01(\t\x12\x0f\n\x07node_id\x18\x02 \x01(\x05\x12\x11\n\ttype_name\x18\x03 \x01(\t\x12\x11\n\tsoc_op_id\x18\x04 \x01(\x05\x12\x12\n\npadding_id\x18\x05 \x01(\x05\x12\x13\n\x0binput_count\x18\x06 \x01(\x05\x12\x14\n\x0coutput_count\x18\x07 \x01(\x05\x1ap\n\rConstNodeInfo\x12\x0c\n\x04name\x18\x01 \x01(\t\x12\x0f\n\x07node_id\x18\x02 \x01(\x05\x12\r\n\x05shape\x18\x03 \x03(\x03\x12\x0c\n\x04\x64\x61ta\x18\x04 \x01(\x0c\x12#\n\x05\x64type\x18\x05 \x01(\x0e\x32\x14.tensorflow.DataType\x1a]\n\rNodeInputInfo\x12\x0f\n\x07node_id\x18\x01 \x01(\x05\x12;\n\nnode_input\x18\x02 \x03(\x0b\x32\'.tensorflow.GraphTransferInfo.NodeInput\x1a\x38\n\x0eNodeOutputInfo\x12\x0f\n\x07node_id\x18\x01 \x01(\x05\x12\x15\n\rmax_byte_size\x18\x02 \x03(\x05\x1aV\n\x12GraphInputNodeInfo\x12\x0c\n\x04name\x18\x01 \x01(\t\x12\r\n\x05shape\x18\x02 \x03(\x03\x12#\n\x05\x64type\x18\x03 \x01(\x0e\x32\x14.tensorflow.DataType\x1aW\n\x13GraphOutputNodeInfo\x12\x0c\n\x04name\x18\x01 \x01(\t\x12\r\n\x05shape\x18\x02 \x03(\x03\x12#\n\x05\x64type\x18\x03 \x01(\x0e\x32\x14.tensorflow.DataType\"#\n\x0b\x44\x65stination\x12\x07\n\x03NOP\x10\x00\x12\x0b\n\x07HEXAGON\x10\x01\x42\x37\n\x18org.tensorflow.frameworkB\x16GraphTransferInfoProtoP\x01\xf8\x01\x01\x62\x06proto3')
  ,
  dependencies=[tensorflow_dot_core_dot_framework_dot_types__pb2.DESCRIPTOR,])



_GRAPHTRANSFERINFO_DESTINATION = _descriptor.EnumDescriptor(
  name='Destination',
  full_name='tensorflow.GraphTransferInfo.Destination',
  filename=None,
  file=DESCRIPTOR,
  values=[
    _descriptor.EnumValueDescriptor(
      name='NOP', index=0, number=0,
      options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='HEXAGON', index=1, number=1,
      options=None,
      type=None),
  ],
  containing_type=None,
  options=None,
  serialized_start=1267,
  serialized_end=1302,
)
_sym_db.RegisterEnumDescriptor(_GRAPHTRANSFERINFO_DESTINATION)


_GRAPHTRANSFERINFO_NODEINPUT = _descriptor.Descriptor(
  name='NodeInput',
  full_name='tensorflow.GraphTransferInfo.NodeInput',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='node_id', full_name='tensorflow.GraphTransferInfo.NodeInput.node_id', index=0,
      number=1, type=5, cpp_type=1, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='output_port', full_name='tensorflow.GraphTransferInfo.NodeInput.output_port', index=1,
      number=2, type=5, cpp_type=1, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=627,
  serialized_end=676,
)

_GRAPHTRANSFERINFO_NODEINFO = _descriptor.Descriptor(
  name='NodeInfo',
  full_name='tensorflow.GraphTransferInfo.NodeInfo',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='name', full_name='tensorflow.GraphTransferInfo.NodeInfo.name', index=0,
      number=1, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='node_id', full_name='tensorflow.GraphTransferInfo.NodeInfo.node_id', index=1,
      number=2, type=5, cpp_type=1, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='type_name', full_name='tensorflow.GraphTransferInfo.NodeInfo.type_name', index=2,
      number=3, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='soc_op_id', full_name='tensorflow.GraphTransferInfo.NodeInfo.soc_op_id', index=3,
      number=4, type=5, cpp_type=1, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='padding_id', full_name='tensorflow.GraphTransferInfo.NodeInfo.padding_id', index=4,
      number=5, type=5, cpp_type=1, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='input_count', full_name='tensorflow.GraphTransferInfo.NodeInfo.input_count', index=5,
      number=6, type=5, cpp_type=1, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='output_count', full_name='tensorflow.GraphTransferInfo.NodeInfo.output_count', index=6,
      number=7, type=5, cpp_type=1, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=679,
  serialized_end=821,
)

_GRAPHTRANSFERINFO_CONSTNODEINFO = _descriptor.Descriptor(
  name='ConstNodeInfo',
  full_name='tensorflow.GraphTransferInfo.ConstNodeInfo',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='name', full_name='tensorflow.GraphTransferInfo.ConstNodeInfo.name', index=0,
      number=1, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='node_id', full_name='tensorflow.GraphTransferInfo.ConstNodeInfo.node_id', index=1,
      number=2, type=5, cpp_type=1, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='shape', full_name='tensorflow.GraphTransferInfo.ConstNodeInfo.shape', index=2,
      number=3, type=3, cpp_type=2, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='data', full_name='tensorflow.GraphTransferInfo.ConstNodeInfo.data', index=3,
      number=4, type=12, cpp_type=9, label=1,
      has_default_value=False, default_value=_b(""),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='dtype', full_name='tensorflow.GraphTransferInfo.ConstNodeInfo.dtype', index=4,
      number=5, type=14, cpp_type=8, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=823,
  serialized_end=935,
)

_GRAPHTRANSFERINFO_NODEINPUTINFO = _descriptor.Descriptor(
  name='NodeInputInfo',
  full_name='tensorflow.GraphTransferInfo.NodeInputInfo',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='node_id', full_name='tensorflow.GraphTransferInfo.NodeInputInfo.node_id', index=0,
      number=1, type=5, cpp_type=1, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='node_input', full_name='tensorflow.GraphTransferInfo.NodeInputInfo.node_input', index=1,
      number=2, type=11, cpp_type=10, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=937,
  serialized_end=1030,
)

_GRAPHTRANSFERINFO_NODEOUTPUTINFO = _descriptor.Descriptor(
  name='NodeOutputInfo',
  full_name='tensorflow.GraphTransferInfo.NodeOutputInfo',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='node_id', full_name='tensorflow.GraphTransferInfo.NodeOutputInfo.node_id', index=0,
      number=1, type=5, cpp_type=1, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='max_byte_size', full_name='tensorflow.GraphTransferInfo.NodeOutputInfo.max_byte_size', index=1,
      number=2, type=5, cpp_type=1, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=1032,
  serialized_end=1088,
)

_GRAPHTRANSFERINFO_GRAPHINPUTNODEINFO = _descriptor.Descriptor(
  name='GraphInputNodeInfo',
  full_name='tensorflow.GraphTransferInfo.GraphInputNodeInfo',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='name', full_name='tensorflow.GraphTransferInfo.GraphInputNodeInfo.name', index=0,
      number=1, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='shape', full_name='tensorflow.GraphTransferInfo.GraphInputNodeInfo.shape', index=1,
      number=2, type=3, cpp_type=2, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='dtype', full_name='tensorflow.GraphTransferInfo.GraphInputNodeInfo.dtype', index=2,
      number=3, type=14, cpp_type=8, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=1090,
  serialized_end=1176,
)

_GRAPHTRANSFERINFO_GRAPHOUTPUTNODEINFO = _descriptor.Descriptor(
  name='GraphOutputNodeInfo',
  full_name='tensorflow.GraphTransferInfo.GraphOutputNodeInfo',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='name', full_name='tensorflow.GraphTransferInfo.GraphOutputNodeInfo.name', index=0,
      number=1, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='shape', full_name='tensorflow.GraphTransferInfo.GraphOutputNodeInfo.shape', index=1,
      number=2, type=3, cpp_type=2, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='dtype', full_name='tensorflow.GraphTransferInfo.GraphOutputNodeInfo.dtype', index=2,
      number=3, type=14, cpp_type=8, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=1178,
  serialized_end=1265,
)

_GRAPHTRANSFERINFO = _descriptor.Descriptor(
  name='GraphTransferInfo',
  full_name='tensorflow.GraphTransferInfo',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='node_info', full_name='tensorflow.GraphTransferInfo.node_info', index=0,
      number=1, type=11, cpp_type=10, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='const_node_info', full_name='tensorflow.GraphTransferInfo.const_node_info', index=1,
      number=2, type=11, cpp_type=10, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='node_input_info', full_name='tensorflow.GraphTransferInfo.node_input_info', index=2,
      number=3, type=11, cpp_type=10, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='node_output_info', full_name='tensorflow.GraphTransferInfo.node_output_info', index=3,
      number=4, type=11, cpp_type=10, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='graph_input_node_info', full_name='tensorflow.GraphTransferInfo.graph_input_node_info', index=4,
      number=5, type=11, cpp_type=10, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='graph_output_node_info', full_name='tensorflow.GraphTransferInfo.graph_output_node_info', index=5,
      number=6, type=11, cpp_type=10, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='destination', full_name='tensorflow.GraphTransferInfo.destination', index=6,
      number=7, type=14, cpp_type=8, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
  ],
  extensions=[
  ],
  nested_types=[_GRAPHTRANSFERINFO_NODEINPUT, _GRAPHTRANSFERINFO_NODEINFO, _GRAPHTRANSFERINFO_CONSTNODEINFO, _GRAPHTRANSFERINFO_NODEINPUTINFO, _GRAPHTRANSFERINFO_NODEOUTPUTINFO, _GRAPHTRANSFERINFO_GRAPHINPUTNODEINFO, _GRAPHTRANSFERINFO_GRAPHOUTPUTNODEINFO, ],
  enum_types=[
    _GRAPHTRANSFERINFO_DESTINATION,
  ],
  options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=107,
  serialized_end=1302,
)

_GRAPHTRANSFERINFO_NODEINPUT.containing_type = _GRAPHTRANSFERINFO
_GRAPHTRANSFERINFO_NODEINFO.containing_type = _GRAPHTRANSFERINFO
_GRAPHTRANSFERINFO_CONSTNODEINFO.fields_by_name['dtype'].enum_type = tensorflow_dot_core_dot_framework_dot_types__pb2._DATATYPE
_GRAPHTRANSFERINFO_CONSTNODEINFO.containing_type = _GRAPHTRANSFERINFO
_GRAPHTRANSFERINFO_NODEINPUTINFO.fields_by_name['node_input'].message_type = _GRAPHTRANSFERINFO_NODEINPUT
_GRAPHTRANSFERINFO_NODEINPUTINFO.containing_type = _GRAPHTRANSFERINFO
_GRAPHTRANSFERINFO_NODEOUTPUTINFO.containing_type = _GRAPHTRANSFERINFO
_GRAPHTRANSFERINFO_GRAPHINPUTNODEINFO.fields_by_name['dtype'].enum_type = tensorflow_dot_core_dot_framework_dot_types__pb2._DATATYPE
_GRAPHTRANSFERINFO_GRAPHINPUTNODEINFO.containing_type = _GRAPHTRANSFERINFO
_GRAPHTRANSFERINFO_GRAPHOUTPUTNODEINFO.fields_by_name['dtype'].enum_type = tensorflow_dot_core_dot_framework_dot_types__pb2._DATATYPE
_GRAPHTRANSFERINFO_GRAPHOUTPUTNODEINFO.containing_type = _GRAPHTRANSFERINFO
_GRAPHTRANSFERINFO.fields_by_name['node_info'].message_type = _GRAPHTRANSFERINFO_NODEINFO
_GRAPHTRANSFERINFO.fields_by_name['const_node_info'].message_type = _GRAPHTRANSFERINFO_CONSTNODEINFO
_GRAPHTRANSFERINFO.fields_by_name['node_input_info'].message_type = _GRAPHTRANSFERINFO_NODEINPUTINFO
_GRAPHTRANSFERINFO.fields_by_name['node_output_info'].message_type = _GRAPHTRANSFERINFO_NODEOUTPUTINFO
_GRAPHTRANSFERINFO.fields_by_name['graph_input_node_info'].message_type = _GRAPHTRANSFERINFO_GRAPHINPUTNODEINFO
_GRAPHTRANSFERINFO.fields_by_name['graph_output_node_info'].message_type = _GRAPHTRANSFERINFO_GRAPHOUTPUTNODEINFO
_GRAPHTRANSFERINFO.fields_by_name['destination'].enum_type = _GRAPHTRANSFERINFO_DESTINATION
_GRAPHTRANSFERINFO_DESTINATION.containing_type = _GRAPHTRANSFERINFO
DESCRIPTOR.message_types_by_name['GraphTransferInfo'] = _GRAPHTRANSFERINFO
_sym_db.RegisterFileDescriptor(DESCRIPTOR)

GraphTransferInfo = _reflection.GeneratedProtocolMessageType('GraphTransferInfo', (_message.Message,), dict(

  NodeInput = _reflection.GeneratedProtocolMessageType('NodeInput', (_message.Message,), dict(
    DESCRIPTOR = _GRAPHTRANSFERINFO_NODEINPUT,
    __module__ = 'tensorflow.core.framework.graph_transfer_info_pb2'
    # @@protoc_insertion_point(class_scope:tensorflow.GraphTransferInfo.NodeInput)
    ))
  ,

  NodeInfo = _reflection.GeneratedProtocolMessageType('NodeInfo', (_message.Message,), dict(
    DESCRIPTOR = _GRAPHTRANSFERINFO_NODEINFO,
    __module__ = 'tensorflow.core.framework.graph_transfer_info_pb2'
    # @@protoc_insertion_point(class_scope:tensorflow.GraphTransferInfo.NodeInfo)
    ))
  ,

  ConstNodeInfo = _reflection.GeneratedProtocolMessageType('ConstNodeInfo', (_message.Message,), dict(
    DESCRIPTOR = _GRAPHTRANSFERINFO_CONSTNODEINFO,
    __module__ = 'tensorflow.core.framework.graph_transfer_info_pb2'
    # @@protoc_insertion_point(class_scope:tensorflow.GraphTransferInfo.ConstNodeInfo)
    ))
  ,

  NodeInputInfo = _reflection.GeneratedProtocolMessageType('NodeInputInfo', (_message.Message,), dict(
    DESCRIPTOR = _GRAPHTRANSFERINFO_NODEINPUTINFO,
    __module__ = 'tensorflow.core.framework.graph_transfer_info_pb2'
    # @@protoc_insertion_point(class_scope:tensorflow.GraphTransferInfo.NodeInputInfo)
    ))
  ,

  NodeOutputInfo = _reflection.GeneratedProtocolMessageType('NodeOutputInfo', (_message.Message,), dict(
    DESCRIPTOR = _GRAPHTRANSFERINFO_NODEOUTPUTINFO,
    __module__ = 'tensorflow.core.framework.graph_transfer_info_pb2'
    # @@protoc_insertion_point(class_scope:tensorflow.GraphTransferInfo.NodeOutputInfo)
    ))
  ,

  GraphInputNodeInfo = _reflection.GeneratedProtocolMessageType('GraphInputNodeInfo', (_message.Message,), dict(
    DESCRIPTOR = _GRAPHTRANSFERINFO_GRAPHINPUTNODEINFO,
    __module__ = 'tensorflow.core.framework.graph_transfer_info_pb2'
    # @@protoc_insertion_point(class_scope:tensorflow.GraphTransferInfo.GraphInputNodeInfo)
    ))
  ,

  GraphOutputNodeInfo = _reflection.GeneratedProtocolMessageType('GraphOutputNodeInfo', (_message.Message,), dict(
    DESCRIPTOR = _GRAPHTRANSFERINFO_GRAPHOUTPUTNODEINFO,
    __module__ = 'tensorflow.core.framework.graph_transfer_info_pb2'
    # @@protoc_insertion_point(class_scope:tensorflow.GraphTransferInfo.GraphOutputNodeInfo)
    ))
  ,
  DESCRIPTOR = _GRAPHTRANSFERINFO,
  __module__ = 'tensorflow.core.framework.graph_transfer_info_pb2'
  # @@protoc_insertion_point(class_scope:tensorflow.GraphTransferInfo)
  ))
_sym_db.RegisterMessage(GraphTransferInfo)
_sym_db.RegisterMessage(GraphTransferInfo.NodeInput)
_sym_db.RegisterMessage(GraphTransferInfo.NodeInfo)
_sym_db.RegisterMessage(GraphTransferInfo.ConstNodeInfo)
_sym_db.RegisterMessage(GraphTransferInfo.NodeInputInfo)
_sym_db.RegisterMessage(GraphTransferInfo.NodeOutputInfo)
_sym_db.RegisterMessage(GraphTransferInfo.GraphInputNodeInfo)
_sym_db.RegisterMessage(GraphTransferInfo.GraphOutputNodeInfo)


DESCRIPTOR.has_options = True
DESCRIPTOR._options = _descriptor._ParseOptions(descriptor_pb2.FileOptions(), _b('\n\030org.tensorflow.frameworkB\026GraphTransferInfoProtoP\001\370\001\001'))
# @@protoc_insertion_point(module_scope)
