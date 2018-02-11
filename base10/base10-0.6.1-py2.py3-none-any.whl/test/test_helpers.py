import pytest
from time import time

from base10 import MetricHelper, MetricHandler
from base10.base import Metric
from base10.exceptions import Base10Error


class TestMetricHelper:
    def setup_method(self):
        self.metric_name = 'metric'
        self.metric_fields = ['value']
        self.metric_metadata = ['hostname']
        self.metric_values = {'value': 0, 'hostname': 'test', 'time': time()}

    def test_metric_helper(self):
        class MyMetric(MetricHelper):
            _name = self.metric_name
            _fields = self.metric_fields
            _metadata = self.metric_metadata

        metric = MyMetric(**self.metric_values)

        assert isinstance(metric, Metric)

        assert metric.name == self.metric_name
        assert metric.fields == self.metric_fields
        assert metric.metadata == self.metric_metadata
        assert metric.values == self.metric_values

    def test_metric_helper_name_exception(self):
        class MyMetric(MetricHelper):
            _fields = self.metric_fields
            _metadata = self.metric_metadata

        with pytest.raises(Base10Error) as exc:
            metric = MyMetric(**self.metric_values)

        assert '_name is required' == str(exc.value)

    def test_metric_helper_fields_exception(self):
        class MyMetric(MetricHelper):
            _name = self.metric_name
            _metadata = self.metric_metadata

        with pytest.raises(Base10Error) as exc:
            metric = MyMetric(**self.metric_values)

        assert '_fields is required' == str(exc.value)

    def test_metric_helper_metadata_exception(self):
        class MyMetric(MetricHelper):
            _name = self.metric_name
            _fields = self.metric_fields

        with pytest.raises(Base10Error) as exc:
            metric = MyMetric(**self.metric_values)

        assert '_metadata is required' == str(exc.value)

    def test_metric_helper_handles_time_field(self):
        class MyMetric(MetricHelper):
            _name = self.metric_name
            _fields = self.metric_fields + ['time']
            _metadata = self.metric_metadata

        metric = MyMetric(**self.metric_values)

        assert metric.fields == self.metric_fields

    def test_metric_helper_kwargs(self):
        class MyMetric(MetricHelper):
            _name = self.metric_name
            _fields = self.metric_fields
            _metadata = self.metric_metadata

        alternative_name = 'test1'
        alternative_fields = ['value1']
        alternative_metadata = ['hostname1']
        alternative_values = {'value1': 0, 'hostname1': 'test', 'time': time()}

        metric = MetricHelper(
            name=alternative_name,
            fields=alternative_fields,
            metadata=alternative_metadata,
            **alternative_values
        )

        assert isinstance(metric, Metric)

        assert metric.name == alternative_name
        assert metric.fields == alternative_fields
        assert metric.metadata == alternative_metadata
        assert metric.values == alternative_values


class TestMetricHandler:
    def test_metric_handler_no_reader_writer(self):
        class Handler(MetricHandler):
            pass

        with pytest.raises(Base10Error) as exc:
            handler = Handler()

        assert 'Either _reader or _writer is required' == str(exc.value)

    def test_metric_handler_no_dialect_with_reader(self):
        class Handler(MetricHandler):
            _reader = None

        with pytest.raises(Base10Error) as exc:
            handler = Handler()

        assert '_dialect is required' == str(exc.value)

    def test_metric_handler_no_dialect_with_writer(self):
        class Handler(MetricHandler):
            _writer = None

        with pytest.raises(Base10Error) as exc:
            handler = Handler()

        assert '_dialect is required' == str(exc.value)

    def test_metric_handler_write_to_read_only(self):
        class Handler(MetricHandler):
            _reader = None
            _dialect = None

        with pytest.raises(Base10Error) as exc:
            handler = Handler()
            handler.write(None)

        assert 'Attempt to write to a read-only MetricHandler' in str(exc.value)

    def test_metric_handler_read_from_write_only(self):
        class Handler(MetricHandler):
            _writer = None
            _dialect = None

        with pytest.raises(Base10Error) as exc:
            handler = Handler()
            metric = next(handler.read())

        assert 'Attempt to read from a write-only MetricHandler' in str(
            exc.value
        )
