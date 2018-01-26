# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: tensorflow/contrib/tensorboard/plugins/trace/trace_info.proto

import sys
_b=sys.version_info[0]<3 and (lambda x:x) or (lambda x:x.encode('latin1'))
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
from google.protobuf import descriptor_pb2
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor.FileDescriptor(
  name='tensorflow/contrib/tensorboard/plugins/trace/trace_info.proto',
  package='tensorflow.contrib.tensorboard',
  syntax='proto3',
  serialized_pb=_b('\n=tensorflow/contrib/tensorboard/plugins/trace/trace_info.proto\x12\x1etensorflow.contrib.tensorboard\"y\n\tTraceInfo\x12\x33\n\x03ops\x18\x01 \x03(\x0b\x32&.tensorflow.contrib.tensorboard.OpInfo\x12\x37\n\x05\x66iles\x18\x02 \x03(\x0b\x32(.tensorflow.contrib.tensorboard.FileInfo\"\xee\x01\n\x06OpInfo\x12\x0c\n\x04name\x18\x01 \x01(\t\x12\x0f\n\x07op_type\x18\x02 \x01(\t\x12\x0e\n\x06\x64\x65vice\x18\x03 \x01(\t\x12<\n\ttraceback\x18\x04 \x03(\x0b\x32).tensorflow.contrib.tensorboard.LineTrace\x12:\n\x06inputs\x18\x05 \x03(\x0b\x32*.tensorflow.contrib.tensorboard.TensorInfo\x12;\n\x07outputs\x18\x06 \x03(\x0b\x32*.tensorflow.contrib.tensorboard.TensorInfo\"3\n\tLineTrace\x12\x11\n\tfile_path\x18\x01 \x01(\t\x12\x13\n\x0bline_number\x18\x02 \x01(\r\"Y\n\nTensorInfo\x12\r\n\x05shape\x18\x01 \x03(\x05\x12\r\n\x05\x64type\x18\x02 \x01(\t\x12\x1a\n\x12num_bytes_per_elem\x18\x03 \x01(\r\x12\x11\n\tconsumers\x18\x04 \x03(\t\"\xcf\x01\n\x08\x46ileInfo\x12\x11\n\tfile_path\x18\x01 \x01(\t\x12\x13\n\x0bsource_code\x18\x02 \x01(\t\x12_\n\x14multiline_statements\x18\x03 \x03(\x0b\x32\x41.tensorflow.contrib.tensorboard.FileInfo.MultilineStatementsEntry\x1a:\n\x18MultilineStatementsEntry\x12\x0b\n\x03key\x18\x01 \x01(\r\x12\r\n\x05value\x18\x02 \x01(\r:\x02\x38\x01\x62\x06proto3')
)




_TRACEINFO = _descriptor.Descriptor(
  name='TraceInfo',
  full_name='tensorflow.contrib.tensorboard.TraceInfo',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='ops', full_name='tensorflow.contrib.tensorboard.TraceInfo.ops', index=0,
      number=1, type=11, cpp_type=10, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='files', full_name='tensorflow.contrib.tensorboard.TraceInfo.files', index=1,
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
  serialized_start=97,
  serialized_end=218,
)


_OPINFO = _descriptor.Descriptor(
  name='OpInfo',
  full_name='tensorflow.contrib.tensorboard.OpInfo',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='name', full_name='tensorflow.contrib.tensorboard.OpInfo.name', index=0,
      number=1, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='op_type', full_name='tensorflow.contrib.tensorboard.OpInfo.op_type', index=1,
      number=2, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='device', full_name='tensorflow.contrib.tensorboard.OpInfo.device', index=2,
      number=3, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='traceback', full_name='tensorflow.contrib.tensorboard.OpInfo.traceback', index=3,
      number=4, type=11, cpp_type=10, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='inputs', full_name='tensorflow.contrib.tensorboard.OpInfo.inputs', index=4,
      number=5, type=11, cpp_type=10, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='outputs', full_name='tensorflow.contrib.tensorboard.OpInfo.outputs', index=5,
      number=6, type=11, cpp_type=10, label=3,
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
  serialized_start=221,
  serialized_end=459,
)


_LINETRACE = _descriptor.Descriptor(
  name='LineTrace',
  full_name='tensorflow.contrib.tensorboard.LineTrace',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='file_path', full_name='tensorflow.contrib.tensorboard.LineTrace.file_path', index=0,
      number=1, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='line_number', full_name='tensorflow.contrib.tensorboard.LineTrace.line_number', index=1,
      number=2, type=13, cpp_type=3, label=1,
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
  serialized_start=461,
  serialized_end=512,
)


_TENSORINFO = _descriptor.Descriptor(
  name='TensorInfo',
  full_name='tensorflow.contrib.tensorboard.TensorInfo',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='shape', full_name='tensorflow.contrib.tensorboard.TensorInfo.shape', index=0,
      number=1, type=5, cpp_type=1, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='dtype', full_name='tensorflow.contrib.tensorboard.TensorInfo.dtype', index=1,
      number=2, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='num_bytes_per_elem', full_name='tensorflow.contrib.tensorboard.TensorInfo.num_bytes_per_elem', index=2,
      number=3, type=13, cpp_type=3, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='consumers', full_name='tensorflow.contrib.tensorboard.TensorInfo.consumers', index=3,
      number=4, type=9, cpp_type=9, label=3,
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
  serialized_start=514,
  serialized_end=603,
)


_FILEINFO_MULTILINESTATEMENTSENTRY = _descriptor.Descriptor(
  name='MultilineStatementsEntry',
  full_name='tensorflow.contrib.tensorboard.FileInfo.MultilineStatementsEntry',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='key', full_name='tensorflow.contrib.tensorboard.FileInfo.MultilineStatementsEntry.key', index=0,
      number=1, type=13, cpp_type=3, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='value', full_name='tensorflow.contrib.tensorboard.FileInfo.MultilineStatementsEntry.value', index=1,
      number=2, type=13, cpp_type=3, label=1,
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
  options=_descriptor._ParseOptions(descriptor_pb2.MessageOptions(), _b('8\001')),
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=755,
  serialized_end=813,
)

_FILEINFO = _descriptor.Descriptor(
  name='FileInfo',
  full_name='tensorflow.contrib.tensorboard.FileInfo',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='file_path', full_name='tensorflow.contrib.tensorboard.FileInfo.file_path', index=0,
      number=1, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='source_code', full_name='tensorflow.contrib.tensorboard.FileInfo.source_code', index=1,
      number=2, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='multiline_statements', full_name='tensorflow.contrib.tensorboard.FileInfo.multiline_statements', index=2,
      number=3, type=11, cpp_type=10, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
  ],
  extensions=[
  ],
  nested_types=[_FILEINFO_MULTILINESTATEMENTSENTRY, ],
  enum_types=[
  ],
  options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=606,
  serialized_end=813,
)

_TRACEINFO.fields_by_name['ops'].message_type = _OPINFO
_TRACEINFO.fields_by_name['files'].message_type = _FILEINFO
_OPINFO.fields_by_name['traceback'].message_type = _LINETRACE
_OPINFO.fields_by_name['inputs'].message_type = _TENSORINFO
_OPINFO.fields_by_name['outputs'].message_type = _TENSORINFO
_FILEINFO_MULTILINESTATEMENTSENTRY.containing_type = _FILEINFO
_FILEINFO.fields_by_name['multiline_statements'].message_type = _FILEINFO_MULTILINESTATEMENTSENTRY
DESCRIPTOR.message_types_by_name['TraceInfo'] = _TRACEINFO
DESCRIPTOR.message_types_by_name['OpInfo'] = _OPINFO
DESCRIPTOR.message_types_by_name['LineTrace'] = _LINETRACE
DESCRIPTOR.message_types_by_name['TensorInfo'] = _TENSORINFO
DESCRIPTOR.message_types_by_name['FileInfo'] = _FILEINFO
_sym_db.RegisterFileDescriptor(DESCRIPTOR)

TraceInfo = _reflection.GeneratedProtocolMessageType('TraceInfo', (_message.Message,), dict(
  DESCRIPTOR = _TRACEINFO,
  __module__ = 'tensorflow.contrib.tensorboard.plugins.trace.trace_info_pb2'
  # @@protoc_insertion_point(class_scope:tensorflow.contrib.tensorboard.TraceInfo)
  ))
_sym_db.RegisterMessage(TraceInfo)

OpInfo = _reflection.GeneratedProtocolMessageType('OpInfo', (_message.Message,), dict(
  DESCRIPTOR = _OPINFO,
  __module__ = 'tensorflow.contrib.tensorboard.plugins.trace.trace_info_pb2'
  # @@protoc_insertion_point(class_scope:tensorflow.contrib.tensorboard.OpInfo)
  ))
_sym_db.RegisterMessage(OpInfo)

LineTrace = _reflection.GeneratedProtocolMessageType('LineTrace', (_message.Message,), dict(
  DESCRIPTOR = _LINETRACE,
  __module__ = 'tensorflow.contrib.tensorboard.plugins.trace.trace_info_pb2'
  # @@protoc_insertion_point(class_scope:tensorflow.contrib.tensorboard.LineTrace)
  ))
_sym_db.RegisterMessage(LineTrace)

TensorInfo = _reflection.GeneratedProtocolMessageType('TensorInfo', (_message.Message,), dict(
  DESCRIPTOR = _TENSORINFO,
  __module__ = 'tensorflow.contrib.tensorboard.plugins.trace.trace_info_pb2'
  # @@protoc_insertion_point(class_scope:tensorflow.contrib.tensorboard.TensorInfo)
  ))
_sym_db.RegisterMessage(TensorInfo)

FileInfo = _reflection.GeneratedProtocolMessageType('FileInfo', (_message.Message,), dict(

  MultilineStatementsEntry = _reflection.GeneratedProtocolMessageType('MultilineStatementsEntry', (_message.Message,), dict(
    DESCRIPTOR = _FILEINFO_MULTILINESTATEMENTSENTRY,
    __module__ = 'tensorflow.contrib.tensorboard.plugins.trace.trace_info_pb2'
    # @@protoc_insertion_point(class_scope:tensorflow.contrib.tensorboard.FileInfo.MultilineStatementsEntry)
    ))
  ,
  DESCRIPTOR = _FILEINFO,
  __module__ = 'tensorflow.contrib.tensorboard.plugins.trace.trace_info_pb2'
  # @@protoc_insertion_point(class_scope:tensorflow.contrib.tensorboard.FileInfo)
  ))
_sym_db.RegisterMessage(FileInfo)
_sym_db.RegisterMessage(FileInfo.MultilineStatementsEntry)


_FILEINFO_MULTILINESTATEMENTSENTRY.has_options = True
_FILEINFO_MULTILINESTATEMENTSENTRY._options = _descriptor._ParseOptions(descriptor_pb2.MessageOptions(), _b('8\001'))
# @@protoc_insertion_point(module_scope)
