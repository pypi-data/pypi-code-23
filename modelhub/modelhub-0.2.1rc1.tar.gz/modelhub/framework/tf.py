# -*- coding: utf-8 -*-
"""
Example

class Model(TFBaseModel):
    model_name="language_detect"
"""
import numpy as np
from .base import BaseModel
from functools import partial
from modelhub.core.utils import cached_property
import modelhub.apis
from modelhub.utils.numpy import pad_constant
from modelhub.core.models import Model

MAX_MESSAGE_LENGTH = int(1 * 1024 * 1024 * 1024)

GRPC_OPTIONS = [
    ('grpc.max_send_message_length', MAX_MESSAGE_LENGTH),
    ('grpc.max_receive_message_length', MAX_MESSAGE_LENGTH)
]


class TFBaseModel(BaseModel):
    TYPE = "TF"

    local_model_version = None

    @cached_property
    def default_schema_name(self):
        import tensorflow as tf
        return tf.saved_model.signature_constants.DEFAULT_SERVING_SIGNATURE_DEF_KEY

    def __init__(
        self,
        run_mode="local",
        hostport=None,
        model_name=None,
        timeout_seconds=5,
        saved_model_path=None,
        local_debug=False,
        tf_debug=False,
        tf_timeline=False,
        local_model_version=None,
        **kwargs
    ):
        super().__init__(**kwargs)
        if model_name is not None:
            self.model_name = model_name
        if local_model_version is not None:
            self.local_model_version = local_model_version

        assert self.model_name
        assert run_mode in ("local", "remote")

        self._run_mode = run_mode

        self._modelhub_model = Model.get_local(self.model_name)
        self._modelhub_version = self._modelhub_model.get_version(self.local_model_version) if self.local_model_version else self._modelhub_model.latest_version
        self._tf_inputs_schema = self._parse_tf_inputs_schema(self._modelhub_version)

        if run_mode == "remote":
            assert hostport, "Must provide hostport when run_mode is remote"
            assert isinstance(hostport, str) or callable(hostport), "hostport can not be type %s, must be a str or a callable" % type(hostport)
            self._prepare_remote(timeout_seconds, hostport)
        elif run_mode == "local":
            self._prepare_local(saved_model_path, local_debug, tf_debug, tf_timeline)
            if local_debug:
                kwargs["verbose"] = True

    def prepare(self):
        pass

    def _prepare_remote(self, timeout_seconds, hostport):
        self.timeout_seconds = timeout_seconds
        from tensorflow_serving.apis import predict_pb2
        from tensorflow.python.framework import tensor_util
        self.PredictRequest = predict_pb2.PredictRequest
        self.tensor_util = tensor_util

        self._hostport = hostport

        import grpc
        from tensorflow_serving.apis import prediction_service_pb2
        stub_builder = lambda hostport_str: prediction_service_pb2.PredictionServiceStub(grpc.insecure_channel(hostport_str, options=GRPC_OPTIONS))

        if isinstance(hostport, str):
            stub = stub_builder(hostport)
            self._stub_fn = lambda: stub
        elif callable(hostport):
            # keep stub in cache in order to maintain long connection
            from functools import lru_cache
            stub_builder = lru_cache(maxsize=100)(stub_builder)

            def _stub_fn():
                hostport_str = hostport(self.model_name, version=self.local_model_version)
                # if hostport_str in stub_cache:
                #     stub = stub_cache[hostport_str]
                # else:
                #     stub = stub_cache.setdefault(hostport_str, stub_builder(hostport_str))
                stub = stub_builder(hostport_str)
                self.log_debug("get stub %s %s", hostport_str, stub)
                return stub

            self._stub_fn = _stub_fn
        else:
            # should not reach here
            raise ValueError("incorrect type of hostport")
        # self._version = Model.get(self.model_name).latest_version

    @property
    def stub(self):
        return self._stub_fn()

    def _prepare_local(self, saved_model_path, local_debug, tf_debug, tf_timeline):
        saved_model_path = saved_model_path or modelhub.apis.get_model_path(self.model_name, version=self.local_model_version, ensure_newest_version=local_debug)
        # from tensorflow. import saved_model_utils
        import tensorflow as tf
        sess = tf.Session(graph=tf.Graph())
        tag_set = ["serve"]
        try:
            meta_graph = tf.saved_model.loader.load(sess, tag_set, saved_model_path)
        except ValueError as e:
            # See https://github.com/tensorflow/tensorflow/issues/10130#issuecomment-303468724
            if e.args and e.args[0].startswith("No op named"):
                sess.close()
                dir(tf.contrib)
                sess = tf.Session(graph=tf.Graph())
                meta_graph = tf.saved_model.loader.load(sess, tag_set, saved_model_path)

        if tf_debug:
            from tensorflow.python.debug.wrappers import local_cli_wrapper

            sess = local_cli_wrapper.LocalCLIDebugWrapperSession(sess)
        self._sess = sess
        self._predict_local = {
            signature_name: self._build_callable(sess, signature_def, tf_timeline)
            for signature_name, signature_def in meta_graph.signature_def.items()
        }
        self._predict_local[None] = self._predict_local[self.default_schema_name]

    def _build_callable(self, sess, signature_def, tf_timeline):
        inputs_names = []
        input_tensor_names = []
        for input_name, input_def in signature_def.inputs.items():
            inputs_names.append(input_name)
            input_tensor_names.append(input_def.name)

        outputs_names = []
        output_tensor_names = []
        for output_name, output_def in signature_def.outputs.items():
            outputs_names.append(output_name)
            output_tensor_names.append(output_def.name)

        if not tf_timeline:
            _callable = sess.make_callable(fetches=output_tensor_names, feed_list=input_tensor_names)
        else:
            import tensorflow as tf
            from uuid import uuid4
            from tensorflow.python.client import timeline

            tf_callable = sess.make_callable(fetches=output_tensor_names, feed_list=input_tensor_names, accept_options=True)
            tf_options = tf.RunOptions(trace_level=tf.RunOptions.FULL_TRACE)

            def _callable(*inputs):
                run_metadata = tf.RunMetadata()
                res = tf_callable(*inputs, run_metadata=run_metadata, options=tf_options)

                with open('/tmp/timeline.%s.json' % uuid4(), 'w') as f:
                    f.write(timeline.Timeline(run_metadata.step_stats).generate_chrome_trace_format(show_memory=True))
                return res

        def callable(inputs):
            inputs = [inputs[input_name] for input_name in inputs_names]

            return dict(zip(outputs_names, _callable(*inputs)))
        return callable

    @staticmethod
    def tensorshape2tuple(tensorshape):
        return [dim.size for dim in tensorshape.dim]

    def _parse_tf_inputs_schema(self, modelhub_version):
        from tensorflow.python.framework.dtypes import _TF_TO_NP

        saved_model_info = modelhub_version.saved_model_info
        return {
            signature_name: {
                input_name: (_TF_TO_NP[input_def.dtype], self.tensorshape2tuple(input_def.tensor_shape))
                for input_name, input_def in signature_def.inputs.items()
            }
            for signature_name, signature_def in saved_model_info.signature_def.items()
        }

    @staticmethod
    def verify_shape(value, shape):
        if len(value.shape) != len(shape):
            raise ValueError("incompatible rank")
        for i, (dim, def_dim) in enumerate(zip(value.shape, shape)):
            if def_dim == -1 or def_dim == dim:
                continue
            raise ValueError("unequal shape on rank %s" % i)

    def _build_request(self, inputs, schema):
        request = self.PredictRequest()
        request.model_spec.name = self.model_name

        if schema:
            request.model_spec.signature_name = schema
        else:
            schema = "serving_default"

        inputs_schema = self._tf_inputs_schema[schema]
        for key, value in inputs.items():
            input_dtype, input_shape = inputs_schema[key]
            value = np.array(value, dtype=input_dtype)
            self.verify_shape(value, input_shape)
            request.inputs[key].CopyFrom(self.tensor_util.make_tensor_proto(value))
        return request

    def _parse_result(self, response):
        return {key: self.tensor_util.MakeNdarray(tensor) for key, tensor in response.outputs.items()}

    def _predict_sync(self, inputs, schema=None):
        self.log_debug("send %s", inputs)
        request = self._build_request(inputs, schema)
        response = self.stub.Predict(request, self.timeout_seconds)
        result = self._parse_result(response)
        self.log_debug("recv %s", result)
        return result

    def _callback(self, future, callback, inputs):
        parsed_outputs = self._get_parsed_outputs_from_future(future, inputs=inputs)
        self.log_debug("recv %s %s", id(future), parsed_outputs)
        callback and callback(inputs, parsed_outputs)

    def _get_parsed_outputs_from_future(self, future, inputs=None):
        try:
            response = future.result()
        except Exception as e:
            self.on_error(inputs, e)
            raise
        return self._parse_result(response)

    def on_error(self, inputs, exception):
        self.log_error("Error happended for inputs: %s \n %s", inputs, exception)

    def _predict_async(self, inputs, callback=None, schema=None):
        request = self._build_request(inputs, schema)
        future = self.stub.Predict.future(request, self.timeout_seconds)
        self.log_debug("send %s %s", id(future), inputs)
        if callback is not None or self.verbose:
            callback = partial(self._callback, callback=callback, inputs=inputs)
            future.add_done_callback(callback)

        return future

    def is_ready(self):
        return True

    def run_model(self, preprocessed_item):
        schema = preprocessed_item.pop("schema", [None])[0]
        if self._run_mode == "remote":
            return self._predict_sync(preprocessed_item, schema=schema)
        else:
            return self._predict_local[schema](preprocessed_item)

    def run_batch(self, input_generator):
        """
        data should be something like
        [{
            "input1":value,
            "input2":value
        },{
            "input1":value2,
            "input2":value2,
        }]

        """
        # data = self._input_maybe_list(data)
        if self._run_mode == "remote":
            return self._run_batch_remote(input_generator)
        else:
            return self._run_batch_local(input_generator)

    def _run_batch_remote(self, input_generator):
        futures = []
        preprocessed_items = []
        origin_items = []

        for item in input_generator:

            self.validate_input_data(item)
            preprocessed_item = self.preprocess(item)
            schema = preprocessed_item.pop("schema", [None])[0]

            origin_items.append(item)
            preprocessed_items.append(preprocessed_item)
            futures.append(self._predict_async(preprocessed_item, schema=schema))

        results = [
            self.postprocess(self._get_parsed_outputs_from_future(future), origin_item, preprocessed_item)
            for future, origin_item, preprocessed_item in zip(futures, origin_items, preprocessed_items)
        ]
        return results

    def _run_batch_local(self, input_generator):
        preprocessed_items = []
        origin_items = []

        for item in input_generator:
            preprocessed_item = self.preprocess(item)
            schema = preprocessed_item.pop("schema", [None])[0]

            origin_items.append(item)
            preprocessed_items.append(preprocessed_item)

        if not preprocessed_items:
            return []
        batch_size = len(preprocessed_items)
        inputs = {
            key: self._merge_inputs_of_key(preprocessed_items, key)
            for key in preprocessed_item
        }
        outputs = self._predict_local[schema](inputs)
        splited_outputs = {
            key: np.array_split(output, batch_size)
            for key, output in outputs.items()
        }
        keys = splited_outputs.keys()
        results = []
        for origin_item, preprocessed_item, *each_outputs_list in zip(origin_items, preprocessed_items, *splited_outputs.values()):
            each_output = dict(zip(keys, each_outputs_list))
            results.append(self.postprocess(each_output, origin_item, preprocessed_item))
        return results

    def _dynamic_padding(self, array_list):
        if len(array_list) < 2:
            return array_list
        sample_item = array_list[0]
        if not isinstance(array_list, np.ndarray):
            array_list = [np.array(item) for item in array_list]
            sample_item = array_list[0]

        max_shape = list(sample_item.shape[1:])

        for item in array_list:
            for dim, size in enumerate(item.shape[1:]):
                if max_shape[dim] < size:
                    max_shape[dim] = size
        return np.concatenate([
            pad_constant(
                item,
                [(0, 0)] + [(0, max_size - size) for max_size, size in zip(max_shape, item.shape[1:])],
                constant_values=self._get_padding_value(item)
            )
            for item in array_list
        ])

    def _get_padding_value(self, array):
        dtype = array.dtype.type
        if issubclass(dtype, (np.character)):
            return array.flat[:1]
        else:
            return dtype(0)

    def _merge_inputs_of_key(self, items, key):
        datas = [item[key] for item in items]
        return self._dynamic_padding(datas)

    def _pack_data(self, data):
        """
        data -> {
            "input1":value,
            "input2":value
        }
        return -> {
            "input1":[value],
            "input2":[value],
        }
        """
        return {
            k: [v]
            for k, v in data.items()
        }

    def _unpack_data(self, outputs):
        """
        outputs -> {
            "result1":[value]
        }
        return -> {
            "result1":value
        }
        """
        return {
            k: v[0]
            for k, v in outputs.items()
        }

    def validate_input_data(self, raw_input):
        pass

    def api_schema(self):
        # TODO
        return {}

    def _schema_to_docstring(self, schema):
        # TODO
        return schema

    def preprocess(self, raw_input):
        """
        raw_input -> user input, suggest format like this{
            "input1:value,
            "input2":value
        }
        return:
        {
            "input1":[value],
            "input2":[value]
        }
        """
        return self._pack_data(raw_input)

    def postprocess(self, tf_output, raw_input, preprocessed_item):
        """
        tf_output -> {
            "output1":[value],
            "output2":[value]
        }
        raw_input -> one item of user input data
        preprocessed_item-> {
            "input1":[value],
            "input2":[value]
        }
        return:
        {
            "output1":value,
            "output2":value
        }

        """
        return self._unpack_data(tf_output)
