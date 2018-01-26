# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: tensorflow/contrib/boosted_trees/proto/split_info.proto

import sys
_b=sys.version_info[0]<3 and (lambda x:x) or (lambda x:x.encode('latin1'))
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
from google.protobuf import descriptor_pb2
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()


from tensorflow.contrib.boosted_trees.proto import tree_config_pb2 as tensorflow_dot_contrib_dot_boosted__trees_dot_proto_dot_tree__config__pb2


DESCRIPTOR = _descriptor.FileDescriptor(
  name='tensorflow/contrib/boosted_trees/proto/split_info.proto',
  package='tensorflow.boosted_trees.learner',
  syntax='proto3',
  serialized_pb=_b('\n7tensorflow/contrib/boosted_trees/proto/split_info.proto\x12 tensorflow.boosted_trees.learner\x1a\x38tensorflow/contrib/boosted_trees/proto/tree_config.proto\"\xbe\x01\n\tSplitInfo\x12<\n\nsplit_node\x18\x01 \x01(\x0b\x32(.tensorflow.boosted_trees.trees.TreeNode\x12\x38\n\nleft_child\x18\x02 \x01(\x0b\x32$.tensorflow.boosted_trees.trees.Leaf\x12\x39\n\x0bright_child\x18\x03 \x01(\x0b\x32$.tensorflow.boosted_trees.trees.LeafB\x03\xf8\x01\x01\x62\x06proto3')
  ,
  dependencies=[tensorflow_dot_contrib_dot_boosted__trees_dot_proto_dot_tree__config__pb2.DESCRIPTOR,])




_SPLITINFO = _descriptor.Descriptor(
  name='SplitInfo',
  full_name='tensorflow.boosted_trees.learner.SplitInfo',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='split_node', full_name='tensorflow.boosted_trees.learner.SplitInfo.split_node', index=0,
      number=1, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='left_child', full_name='tensorflow.boosted_trees.learner.SplitInfo.left_child', index=1,
      number=2, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='right_child', full_name='tensorflow.boosted_trees.learner.SplitInfo.right_child', index=2,
      number=3, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
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
  serialized_start=152,
  serialized_end=342,
)

_SPLITINFO.fields_by_name['split_node'].message_type = tensorflow_dot_contrib_dot_boosted__trees_dot_proto_dot_tree__config__pb2._TREENODE
_SPLITINFO.fields_by_name['left_child'].message_type = tensorflow_dot_contrib_dot_boosted__trees_dot_proto_dot_tree__config__pb2._LEAF
_SPLITINFO.fields_by_name['right_child'].message_type = tensorflow_dot_contrib_dot_boosted__trees_dot_proto_dot_tree__config__pb2._LEAF
DESCRIPTOR.message_types_by_name['SplitInfo'] = _SPLITINFO
_sym_db.RegisterFileDescriptor(DESCRIPTOR)

SplitInfo = _reflection.GeneratedProtocolMessageType('SplitInfo', (_message.Message,), dict(
  DESCRIPTOR = _SPLITINFO,
  __module__ = 'tensorflow.contrib.boosted_trees.proto.split_info_pb2'
  # @@protoc_insertion_point(class_scope:tensorflow.boosted_trees.learner.SplitInfo)
  ))
_sym_db.RegisterMessage(SplitInfo)


DESCRIPTOR.has_options = True
DESCRIPTOR._options = _descriptor._ParseOptions(descriptor_pb2.FileOptions(), _b('\370\001\001'))
# @@protoc_insertion_point(module_scope)
