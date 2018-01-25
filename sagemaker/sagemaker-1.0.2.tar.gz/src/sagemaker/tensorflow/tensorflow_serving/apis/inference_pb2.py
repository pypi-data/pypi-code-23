# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: tensorflow_serving/apis/inference.proto

import sys
_b=sys.version_info[0]<3 and (lambda x:x) or (lambda x:x.encode('latin1'))
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
from google.protobuf import descriptor_pb2
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()


from tensorflow_serving.apis import classification_pb2 as tensorflow__serving_dot_apis_dot_classification__pb2
from tensorflow_serving.apis import input_pb2 as tensorflow__serving_dot_apis_dot_input__pb2
from tensorflow_serving.apis import model_pb2 as tensorflow__serving_dot_apis_dot_model__pb2
from tensorflow_serving.apis import regression_pb2 as tensorflow__serving_dot_apis_dot_regression__pb2


DESCRIPTOR = _descriptor.FileDescriptor(
  name='tensorflow_serving/apis/inference.proto',
  package='tensorflow.serving',
  syntax='proto3',
  serialized_pb=_b('\n\'tensorflow_serving/apis/inference.proto\x12\x12tensorflow.serving\x1a,tensorflow_serving/apis/classification.proto\x1a#tensorflow_serving/apis/input.proto\x1a#tensorflow_serving/apis/model.proto\x1a(tensorflow_serving/apis/regression.proto\"W\n\rInferenceTask\x12\x31\n\nmodel_spec\x18\x01 \x01(\x0b\x32\x1d.tensorflow.serving.ModelSpec\x12\x13\n\x0bmethod_name\x18\x02 \x01(\t\"\xdc\x01\n\x0fInferenceResult\x12\x31\n\nmodel_spec\x18\x01 \x01(\x0b\x32\x1d.tensorflow.serving.ModelSpec\x12I\n\x15\x63lassification_result\x18\x02 \x01(\x0b\x32(.tensorflow.serving.ClassificationResultH\x00\x12\x41\n\x11regression_result\x18\x03 \x01(\x0b\x32$.tensorflow.serving.RegressionResultH\x00\x42\x08\n\x06result\"s\n\x15MultiInferenceRequest\x12\x30\n\x05tasks\x18\x01 \x03(\x0b\x32!.tensorflow.serving.InferenceTask\x12(\n\x05input\x18\x02 \x01(\x0b\x32\x19.tensorflow.serving.Input\"N\n\x16MultiInferenceResponse\x12\x34\n\x07results\x18\x01 \x03(\x0b\x32#.tensorflow.serving.InferenceResultB\x03\xf8\x01\x01\x62\x06proto3')
  ,
  dependencies=[tensorflow__serving_dot_apis_dot_classification__pb2.DESCRIPTOR,tensorflow__serving_dot_apis_dot_input__pb2.DESCRIPTOR,tensorflow__serving_dot_apis_dot_model__pb2.DESCRIPTOR,tensorflow__serving_dot_apis_dot_regression__pb2.DESCRIPTOR,])




_INFERENCETASK = _descriptor.Descriptor(
  name='InferenceTask',
  full_name='tensorflow.serving.InferenceTask',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='model_spec', full_name='tensorflow.serving.InferenceTask.model_spec', index=0,
      number=1, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='method_name', full_name='tensorflow.serving.InferenceTask.method_name', index=1,
      number=2, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
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
  serialized_start=225,
  serialized_end=312,
)


_INFERENCERESULT = _descriptor.Descriptor(
  name='InferenceResult',
  full_name='tensorflow.serving.InferenceResult',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='model_spec', full_name='tensorflow.serving.InferenceResult.model_spec', index=0,
      number=1, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='classification_result', full_name='tensorflow.serving.InferenceResult.classification_result', index=1,
      number=2, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='regression_result', full_name='tensorflow.serving.InferenceResult.regression_result', index=2,
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
    _descriptor.OneofDescriptor(
      name='result', full_name='tensorflow.serving.InferenceResult.result',
      index=0, containing_type=None, fields=[]),
  ],
  serialized_start=315,
  serialized_end=535,
)


_MULTIINFERENCEREQUEST = _descriptor.Descriptor(
  name='MultiInferenceRequest',
  full_name='tensorflow.serving.MultiInferenceRequest',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='tasks', full_name='tensorflow.serving.MultiInferenceRequest.tasks', index=0,
      number=1, type=11, cpp_type=10, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='input', full_name='tensorflow.serving.MultiInferenceRequest.input', index=1,
      number=2, type=11, cpp_type=10, label=1,
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
  serialized_start=537,
  serialized_end=652,
)


_MULTIINFERENCERESPONSE = _descriptor.Descriptor(
  name='MultiInferenceResponse',
  full_name='tensorflow.serving.MultiInferenceResponse',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='results', full_name='tensorflow.serving.MultiInferenceResponse.results', index=0,
      number=1, type=11, cpp_type=10, label=3,
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
  serialized_start=654,
  serialized_end=732,
)

_INFERENCETASK.fields_by_name['model_spec'].message_type = tensorflow__serving_dot_apis_dot_model__pb2._MODELSPEC
_INFERENCERESULT.fields_by_name['model_spec'].message_type = tensorflow__serving_dot_apis_dot_model__pb2._MODELSPEC
_INFERENCERESULT.fields_by_name['classification_result'].message_type = tensorflow__serving_dot_apis_dot_classification__pb2._CLASSIFICATIONRESULT
_INFERENCERESULT.fields_by_name['regression_result'].message_type = tensorflow__serving_dot_apis_dot_regression__pb2._REGRESSIONRESULT
_INFERENCERESULT.oneofs_by_name['result'].fields.append(
  _INFERENCERESULT.fields_by_name['classification_result'])
_INFERENCERESULT.fields_by_name['classification_result'].containing_oneof = _INFERENCERESULT.oneofs_by_name['result']
_INFERENCERESULT.oneofs_by_name['result'].fields.append(
  _INFERENCERESULT.fields_by_name['regression_result'])
_INFERENCERESULT.fields_by_name['regression_result'].containing_oneof = _INFERENCERESULT.oneofs_by_name['result']
_MULTIINFERENCEREQUEST.fields_by_name['tasks'].message_type = _INFERENCETASK
_MULTIINFERENCEREQUEST.fields_by_name['input'].message_type = tensorflow__serving_dot_apis_dot_input__pb2._INPUT
_MULTIINFERENCERESPONSE.fields_by_name['results'].message_type = _INFERENCERESULT
DESCRIPTOR.message_types_by_name['InferenceTask'] = _INFERENCETASK
DESCRIPTOR.message_types_by_name['InferenceResult'] = _INFERENCERESULT
DESCRIPTOR.message_types_by_name['MultiInferenceRequest'] = _MULTIINFERENCEREQUEST
DESCRIPTOR.message_types_by_name['MultiInferenceResponse'] = _MULTIINFERENCERESPONSE
_sym_db.RegisterFileDescriptor(DESCRIPTOR)

InferenceTask = _reflection.GeneratedProtocolMessageType('InferenceTask', (_message.Message,), dict(
  DESCRIPTOR = _INFERENCETASK,
  __module__ = 'tensorflow_serving.apis.inference_pb2'
  # @@protoc_insertion_point(class_scope:tensorflow.serving.InferenceTask)
  ))
_sym_db.RegisterMessage(InferenceTask)

InferenceResult = _reflection.GeneratedProtocolMessageType('InferenceResult', (_message.Message,), dict(
  DESCRIPTOR = _INFERENCERESULT,
  __module__ = 'tensorflow_serving.apis.inference_pb2'
  # @@protoc_insertion_point(class_scope:tensorflow.serving.InferenceResult)
  ))
_sym_db.RegisterMessage(InferenceResult)

MultiInferenceRequest = _reflection.GeneratedProtocolMessageType('MultiInferenceRequest', (_message.Message,), dict(
  DESCRIPTOR = _MULTIINFERENCEREQUEST,
  __module__ = 'tensorflow_serving.apis.inference_pb2'
  # @@protoc_insertion_point(class_scope:tensorflow.serving.MultiInferenceRequest)
  ))
_sym_db.RegisterMessage(MultiInferenceRequest)

MultiInferenceResponse = _reflection.GeneratedProtocolMessageType('MultiInferenceResponse', (_message.Message,), dict(
  DESCRIPTOR = _MULTIINFERENCERESPONSE,
  __module__ = 'tensorflow_serving.apis.inference_pb2'
  # @@protoc_insertion_point(class_scope:tensorflow.serving.MultiInferenceResponse)
  ))
_sym_db.RegisterMessage(MultiInferenceResponse)


DESCRIPTOR.has_options = True
DESCRIPTOR._options = _descriptor._ParseOptions(descriptor_pb2.FileOptions(), _b('\370\001\001'))
# @@protoc_insertion_point(module_scope)
