from typing import List, Dict, Union
from itertools import chain
from datetime import datetime, timedelta
from inspect import isabstract
from functools import reduce

from anji_orm import register, Model, IntField, DatetimeField, FloatField, DictField, ListField, QueryAst
from lazy import lazy
import rethinkdb as R

from .types import FieldMark, TimeseriesCompressPolicy

__author__ = "Bogdan Gladyshev"
__copyright__ = "Copyright 2017, Bogdan Gladyshev"
__credits__ = ["Bogdan Gladyshev"]
__license__ = "MIT"
__version__ = "0.8.9"
__maintainer__ = "Bogdan Gladyshev"
__email__ = "siredvin.dark@gmail.com"
__status__ = "Production"


class TimeSeriesMixinException(Exception):
    pass


class TimeSeriesCompressException(Exception):
    pass


class TimeSeriesMixin(Model):

    def root_mean_square(self):
        """
        Predict next time value based on two phase "Root mean square" algorithm
        """
        weight_field = self._field_marks.get(FieldMark.timeseries_weight, None)
        value_field = self._field_marks.get(FieldMark.timeseries_value, None)
        if value_field is None:
            raise TimeSeriesMixinException("Value field must be defined with field mark!")
        model_query = self.db_query(self.additional_statistic_filter(self.build_similarity_query()))
        if weight_field:
            model_query = model_query.map(lambda data: {'value': data[value_field], 'weight': data[weight_field]})
        else:
            model_query = model_query.map(lambda data: {'value': data[value_field], 'weight': 1})
        model_stats = self.execute(model_query)
        if hasattr(self, '_compressed_stat_model'):
            compressed_stat_model = self._compressed_stat_model
            compress_model_stats = compressed_stat_model.get_data(self)
        else:
            compress_model_stats = []
        return self.shared.statistic.dict_cutoff_rms(list(chain(model_stats, compress_model_stats)))

    @classmethod
    def additional_statistic_filter(cls, current_query: QueryAst) -> QueryAst:
        return current_query

    @lazy
    def timeseries_weight(self):
        return getattr(self, self._field_marks.get(FieldMark.timeseries_weight, ''), 1)

    @lazy
    def timeseries_value(self):
        return getattr(self, self._field_marks[FieldMark.timeseries_value])

    @lazy
    def timeseries_timestamp(self):
        return getattr(self, self._field_marks[FieldMark.timeseries_timestamp])

    @lazy
    def timeseries_rms(self):
        return self.timeseries_value * self.timeseries_value * self.timeseries_weight

    @lazy
    def compressed_primary_key(self):
        result = []
        for value in self._primary_keys:
            result.append(getattr(self, value))
        return result


class TimeSeriesCompressModel(TimeSeriesMixin):

    value = FloatField(field_marks=[FieldMark.timeseries_value])
    weight = IntField(description='Statictis weight', field_marks=[FieldMark.timeseries_weight])
    original_python_info = DictField()
    original_definer_key = ListField(definer=True)
    created_timestamp = DatetimeField(field_marks=[FieldMark.timeseries_timestamp])
    period_start_timestamp = DatetimeField()
    period_end_timestamp = DatetimeField()

    compress_policy = TimeseriesCompressPolicy.simple

    @classmethod
    def get_data(cls, original_model_record: Union[Model, TimeSeriesMixin]):
        compress_model_stats = cls.execute(cls.db_query(
            (cls.original_python_info == original_model_record._build_python_info()) &
            (cls.original_definer_key == original_model_record.compressed_primary_key)
        ).map(lambda data: {'value': data['value'], 'weight': data['weight']}))
        return compress_model_stats

    @classmethod
    def find_original_models(cls) -> List[Union[Model, TimeSeriesMixin]]:
        original_model_list = list(
            filter(
                lambda x: hasattr(x, '_compressed_stat_model') and x._compressed_stat_model == cls,
                chain(*register.tables_model_link.values())
            )
        )
        if not original_model_list:
            return None
        if cls.compress_policy == TimeseriesCompressPolicy.simple:
            return original_model_list[:1]
        elif cls.compress_policy == TimeseriesCompressPolicy.class_search:
            original_model_list = list(filter(lambda x: not isabstract(x), original_model_list))
            return original_model_list
        return None

    @classmethod
    def automatic_original_data_compress_for_model(cls, original_model: Union[Model, TimeSeriesMixin], days_before: int, offset: int) -> None:
        original_model_timestamp_field = original_model._field_marks[FieldMark.timeseries_timestamp]
        start_time = R.expr(datetime.now(R.make_timezone("00:00")) - timedelta(days=days_before))
        groups = cls.execute(original_model.unique_groups_query())
        for group in groups:
            base_ast_query = reduce(lambda x, y: x & y, map(lambda field, value: getattr(cls, field) == value, group))
            base_ast_query = original_model.additional_statistic_filter(base_ast_query)
            group_search_query = original_model.db_query(base_ast_query)\
                .filter(R.row[original_model_timestamp_field] <= start_time)\
                .order_by(R.desc('complete_timestamp')).skip(offset)
            group_records = cls.execute(group_search_query)
            if group_records:
                cls.compress_original_data(group_records)

    @classmethod
    def automatic_original_data_compress(cls, days_before: int, offset: int) -> None:
        original_models = cls.find_original_models()
        if not original_models:
            raise TimeSeriesCompressException(f"Class {cls.__name__} not used as compression model")
        for original_model in original_models:
            cls.automatic_original_data_compress_for_model(original_model, days_before, offset)

    @classmethod
    def compress_original_data(cls, original_models: List[Union[Model, TimeSeriesMixin]]) -> 'TimeSeriesCompressModel':
        first_element = original_models[0]
        statistic: 'StatisticEngine' = first_element.shared.statistic
        data_count = len(original_models)
        period_start_timestamp = first_element.timeseries_timestamp
        period_end_timestamp = first_element.timeseries_timestamp
        for original_model in original_models:
            period_start_timestamp = min(period_start_timestamp, original_model.timeseries_timestamp)
            period_end_timestamp = max(period_end_timestamp, original_model.timeseries_timestamp)
        compress_data = dict(
            value=statistic.cutoff_rms(original_models),
            weight=data_count,
            created_timestamp=datetime.now(R.make_timezone("00:00")),
            period_start_timestamp=period_start_timestamp,
            period_end_timestamp=period_end_timestamp,
            original_python_info=first_element._build_python_info(),
            original_definer_key=first_element.compressed_primary_key
        )
        statistic_object = cls(
            **compress_data
        )
        statistic_object.send()
        for original_model in original_models:
            original_model.delete()
        return statistic_object

    @classmethod
    def automatic_compressed_data_compress(cls, statistic: 'StatisticEngine') -> None:
        groups = cls.execute(cls.unique_groups_query())
        for group in groups:
            base_ast_query = reduce(lambda x, y: x & y, map(lambda field, value: getattr(cls, field) == value, group))
            data_list = cls.query(base_ast_query)
            if data_list:
                first_element = data_list[0]
                first_element.value = statistic.cutoff_rms(data_list)
                first_element.weight = sum((x.weight for x in data_list))
                for data_element in data_list[1:]:
                    data_element.delete()
                first_element.send()
                del data_list


class StatisticEngine(object):

    def __init__(self, cutoff):
        self.cutoff = cutoff

    def cutoff_rms(self, values: List[TimeSeriesMixin]) -> float:
        if not values:
            return 0.0
        first_iteration_lenght = sum(x.timeseries_weight for x in values)
        first_iteration_rms = (sum(x.timeseries_rms for x in values) / first_iteration_lenght) ** 0.5
        cutoff_value = first_iteration_rms * self.cutoff
        processed_durations = [x for x in values if x.timeseries_value >= cutoff_value]
        processed_durations_lenght = sum(x.timeseries_weight for x in processed_durations)
        return (sum(x.timeseries_rms for x in processed_durations) / processed_durations_lenght) ** 0.5

    def dict_cutoff_rms(self, values: [Dict]) -> float:
        if not values:
            return 0.0
        first_iteration_lenght = sum(x['weight'] for x in values)
        first_iteration_rms = (sum(x['weight'] * x['value'] * x['value'] for x in values) / first_iteration_lenght) ** 0.5
        cutoff_value = first_iteration_rms * self.cutoff
        processed_durations = [x for x in values if x['value'] >= cutoff_value]
        processed_durations_lenght = sum(x['weight'] for x in processed_durations)
        return (sum(x['weight'] * x['value'] * x['value'] for x in processed_durations) / processed_durations_lenght) ** 0.5
