import datetime
import json

import pytest
import pytz
import responses

from datarobot import BacktestSpecification, DatetimePartitioning, DatetimePartitioningSpecification
from datarobot import partitioning_methods


def test_future_proof(datetime_partition_server_data):
    future_response = dict(datetime_partition_server_data, future='newKey')
    DatetimePartitioning.from_server_data(future_response)


def test_construct_duration_string():
    duration = partitioning_methods.construct_duration_string(years=1, months=2, days=3,
                                                              hours=4, minutes=5, seconds=6)
    assert duration == 'P1Y2M3DT4H5M6S'


def test_construct_duration_string_empty():
    assert partitioning_methods.construct_duration_string() == 'P0Y0M0DT0H0M0S'


def test_collect_payload_fails_cleanly_on_type_error(datetime_partition_spec):
    datetime_partition_spec.holdout_start_date = str(datetime_partition_spec.holdout_start_date)
    with pytest.raises(ValueError) as exc_info:
        datetime_partition_spec.collect_payload()
    assert 'expected holdout_start_date to be a datetime.datetime' in str(exc_info.value)


def test_backtest_to_specification(datetime_partition):
    backtest = datetime_partition.backtests[0]
    backtest_spec = backtest.to_specification()
    assert backtest_spec.index == backtest.index
    assert backtest_spec.gap_duration == backtest.gap_duration
    assert backtest_spec.validation_start_date
    assert backtest_spec.validation_duration == backtest.validation_duration


def test_partition_to_specification(datetime_partition):
    part_spec = datetime_partition.to_specification()
    assert part_spec.datetime_partition_column == datetime_partition.datetime_partition_column
    assert (part_spec.autopilot_data_selection_method ==
            datetime_partition.autopilot_data_selection_method)
    assert part_spec.validation_duration == datetime_partition.validation_duration
    assert part_spec.holdout_start_date == datetime_partition.holdout_start_date
    assert part_spec.holdout_duration == datetime_partition.holdout_duration
    assert part_spec.gap_duration == datetime_partition.gap_duration
    assert part_spec.number_of_backtests == datetime_partition.number_of_backtests
    assert len(part_spec.backtests) == len(datetime_partition.backtests)
    for bt_spec in part_spec.backtests:
        assert isinstance(bt_spec, BacktestSpecification)


@responses.activate
@pytest.mark.usefixtures('client')
def test_retrieve(project_id, project_url, datetime_partition_after_target_server_data):
    responses.add(responses.GET, '{}datetimePartitioning/'.format(project_url),
                  json=datetime_partition_after_target_server_data)

    partition = DatetimePartitioning.get(project_id)

    assert partition.primary_training_row_count == 100
    assert partition.available_training_row_count == 100
    assert partition.gap_row_count == 100
    assert partition.holdout_row_count == 100
    assert partition.total_row_count == 100

    backtest = partition.backtests[0]
    assert backtest.primary_training_row_count == 100
    assert backtest.available_training_row_count == 100
    assert backtest.gap_row_count == 100
    assert backtest.validation_row_count == 100
    assert backtest.total_row_count == 100


@responses.activate
@pytest.mark.usefixtures('client')
def test_generate(project_id, project_url, datetime_partition_server_data,
                  holdout_start_date, datetime_partition_spec):
    responses.add(responses.POST, '{}datetimePartitioning/'.format(project_url),
                  json=datetime_partition_server_data)

    partition = DatetimePartitioning.generate(project_id, datetime_partition_spec)

    # test that we send the right things
    actual_payload = json.loads(responses.calls[0].request.body)
    expected_backtests = [{
        'index': bt.index, 'gapDuration': bt.gap_duration,
        'validationStartDate': bt.validation_start_date.isoformat(),
        'validationDuration': bt.validation_duration
        } for bt in datetime_partition_spec.backtests]
    expected_payload = {
        'datetimePartitionColumn': datetime_partition_spec.datetime_partition_column,
        'autopilotDataSelectionMethod': datetime_partition_spec.autopilot_data_selection_method,
        'validationDuration': datetime_partition_spec.validation_duration,
        'holdoutStartDate': holdout_start_date.isoformat(),
        'holdoutDuration': datetime_partition_spec.holdout_duration,
        'gapDuration': datetime_partition_spec.gap_duration,
        'numberOfBacktests': datetime_partition_spec.number_of_backtests,
        'backtests': expected_backtests
    }
    assert actual_payload == expected_payload

    # test that we get the right thing back
    assert partition.project_id == project_id
    assert (partition.datetime_partition_column ==
            datetime_partition_server_data['datetimePartitionColumn'])
    assert partition.date_format == datetime_partition_server_data['dateFormat']
    assert (partition.autopilot_data_selection_method ==
            datetime_partition_server_data['autopilotDataSelectionMethod'])
    assert partition.validation_duration == datetime_partition_server_data['validationDuration']

    assert isinstance(partition.available_training_start_date, datetime.datetime)
    assert (partition.available_training_duration ==
            datetime_partition_server_data['availableTrainingDuration'])
    assert isinstance(partition.available_training_end_date, datetime.datetime)

    assert isinstance(partition.primary_training_start_date, datetime.datetime)
    assert (partition.primary_training_duration ==
            datetime_partition_server_data['primaryTrainingDuration'])
    assert isinstance(partition.primary_training_end_date, datetime.datetime)

    assert isinstance(partition.gap_start_date, datetime.datetime)
    assert partition.gap_duration == datetime_partition_server_data['gapDuration']
    assert isinstance(partition.gap_end_date, datetime.datetime)

    assert partition.holdout_start_date == holdout_start_date
    assert partition.holdout_duration == datetime_partition_server_data['holdoutDuration']
    assert isinstance(partition.holdout_end_date, datetime.datetime)

    assert partition.number_of_backtests == datetime_partition_server_data['numberOfBacktests']
    [backtest] = partition.backtests
    [backtest_data] = datetime_partition_server_data['backtests']
    assert backtest.index == backtest_data['index']
    assert isinstance(backtest.available_training_start_date, datetime.datetime)
    assert backtest.available_training_duration == backtest_data['availableTrainingDuration']
    assert isinstance(backtest.available_training_end_date, datetime.datetime)
    assert isinstance(backtest.primary_training_start_date, datetime.datetime)
    assert backtest.primary_training_duration == backtest_data['primaryTrainingDuration']
    assert isinstance(backtest.primary_training_end_date, datetime.datetime)
    assert isinstance(backtest.gap_start_date, datetime.datetime)
    assert backtest.gap_duration == backtest_data['gapDuration']
    assert isinstance(backtest.gap_end_date, datetime.datetime)
    assert isinstance(backtest.validation_start_date, datetime.datetime)
    assert backtest.validation_duration == backtest_data['validationDuration']
    assert isinstance(backtest.validation_end_date, datetime.datetime)


@responses.activate
@pytest.mark.usefixtures('client')
def test_retrieve_otp_without_holdout(project_id, project_url,
                                      datetime_partition_without_holdout_server_data):
    responses.add(responses.GET, '{}datetimePartitioning/'.format(project_url),
                  json=datetime_partition_without_holdout_server_data)

    partition = DatetimePartitioning.get(project_id)

    assert partition.primary_training_start_date is None
    assert partition.primary_training_end_date is None
    assert partition.primary_training_row_count == 0
    assert partition.primary_training_duration == 'P0Y0M0D'

    assert partition.available_training_start_date == datetime.datetime(2013, 11, 20, 22, 38, 47,
                                                                        tzinfo=pytz.UTC)
    assert partition.available_training_end_date == datetime.datetime(2014, 1, 12, 22, 44, 23,
                                                                      tzinfo=pytz.UTC)
    assert partition.available_training_duration == 'P0Y0M53DT0H5M36S'
    assert partition.available_training_row_count == 4276

    assert partition.gap_start_date is None
    assert partition.gap_end_date is None
    assert partition.gap_row_count == 0
    assert partition.gap_duration == 'P0Y0M0D'

    assert partition.holdout_start_date is None
    assert partition.holdout_end_date is None
    assert partition.holdout_row_count == 0
    assert partition.holdout_duration == 'P0Y0M0D'

    assert partition.total_row_count == 4276

    backtest = partition.backtests[0]
    assert backtest.primary_training_row_count == 4168
    assert backtest.available_training_row_count == 4168
    assert backtest.gap_row_count == 0
    assert backtest.validation_row_count == 108
    assert backtest.total_row_count == 4276


@responses.activate
@pytest.mark.usefixtures('client')
def test_from_minimum_specification(project_id, project_url, datetime_partition_server_data):
    responses.add(responses.POST, '{}datetimePartitioning/'.format(project_url),
                  json=datetime_partition_server_data)

    min_spec = DatetimePartitioningSpecification(
        datetime_partition_server_data['datetimePartitionColumn'])
    DatetimePartitioning.generate(project_id, min_spec)

    expected_data = {'datetimePartitionColumn':
                     datetime_partition_server_data['datetimePartitionColumn']}
    assert responses.calls[0].request.body == json.dumps(expected_data)


def test_to_dataframe(datetime_partition):
    df = datetime_partition.to_dataframe()
    expected_shape = (4*(1+datetime_partition.number_of_backtests), 3)
    assert df.shape == expected_shape
