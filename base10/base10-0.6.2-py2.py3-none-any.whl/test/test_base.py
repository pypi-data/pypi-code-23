import pytest
from time import time

from base10.base import Dialect, Metric, Reader, Writer
from base10.exceptions import DialectError


class TestDialects:
    def test_dialect_construction(self):
        assert isinstance(Dialect(), Dialect)

    def test_dialect_from_string_exception(self):
        dialect = Dialect()

        with pytest.raises(DialectError) as exc:
            dialect.from_string('')

        assert 'Attempt to read with a write-only dialect' == str(exc.value)

    def test_dialect_to_string_exception(self):
        dialect = Dialect()

        with pytest.raises(DialectError) as exc:
            dialect.to_string(None)

        assert 'Attempt to write with a read-only dialect' == str(exc.value)


class TestMetrics:
    def setup_method(self):
        self.metric_name = 'metric'
        self.metric_fields = ['value']
        self.metric_metadata = ['hostname']
        self.metric_values = {'value': 0, 'hostname': 'test', 'time': time()}

    def test_metric_properties(self):
        metric = Metric(
            self.metric_name, self.metric_fields, self.metric_metadata,
            **self.metric_values
        )

        assert metric.name == self.metric_name
        assert metric.fields == self.metric_fields
        assert metric.metadata == self.metric_metadata
        assert metric.values == self.metric_values

    def test_metric_handle_time_field(self):
        metric = Metric(
            self.metric_name, self.metric_fields + ['time'],
            self.metric_metadata, **self.metric_values
        )

        assert 'time' not in metric.fields

    def test_metric_add_time(self):
        alternative_values = {
            'value': 0,
            'hostname': 'test'
        }  # Note: No explicit time

        metric = Metric(
            self.metric_name, self.metric_fields, self.metric_metadata,
            **alternative_values
        )

        assert 'time' in metric.values

    def test_metric_repr(self):
        import re
        from ast import literal_eval

        metric = Metric(
            self.metric_name, self.metric_fields, self.metric_metadata,
            **self.metric_values
        )

        regex = '<Metric:"([^"]+)" Fields:(\[[^\]]+\]) Metadata:(\[[^\]]+\]) Values:({[^}]+})>'

        match = re.match(regex, repr(metric))

        assert match is not None
        assert match.lastindex == 4
        assert match.group(1) == self.metric_name
        assert literal_eval(match.group(2)) == self.metric_fields
        assert literal_eval(match.group(3)) == self.metric_metadata
        assert literal_eval(match.group(4)) == self.metric_values

    def test_metric_name_exception(self):
        alternative_values = {
            'value': 0,
            'host': 'test',
            'time': time()
        }  # Note: "host" not "hostname"

        with pytest.raises(NameError) as exc:
            metric = Metric(
                self.metric_name, self.metric_fields, self.metric_metadata,
                **alternative_values
            )

        assert "Expected ['hostname', 'value'] but got ['host', 'value']" in str(
            exc.value
        )


class TestTransports:
    def test_reader_construction(self):
        with pytest.raises(TypeError) as exc:
            reader = Reader()

        assert "Can't instantiate" in str(exc.value)

    def test_writer_construction(self):
        with pytest.raises(TypeError) as exc:
            writer = Writer()

        assert "Can't instantiate" in str(exc.value)
