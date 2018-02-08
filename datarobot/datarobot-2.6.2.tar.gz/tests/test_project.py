# coding=utf-8
import datetime
import json
import re

import mock
import pandas as pd
import pytest
import responses
import six

from datarobot import (Project,
                       Blueprint,
                       AUTOPILOT_MODE,
                       Model,
                       ModelJob,
                       Featurelist,
                       PredictJob,
                       AdvancedOptions,
                       UserCV,
                       UserTVH,
                       QUEUE_STATUS,
                       errors)
from datarobot.enums import PROJECT_STAGE

from .test_helpers import URLParamsTestCase, fixture_file_path
from .utils import SDKTestcase, assertJsonEq, assert_raised_regex

if six.PY3:
    from unittest.mock import patch
else:
    from mock import patch

# FIXTURES and HELPERS #############################################################################


def construct_dummy_aimed_project(
    pid='p-id',
    project_name='Untitled Project',
    target='SalePrice',
    autopilot_mode=0
):
    return {
        'id': pid,
        'projectName': project_name,
        'fileName': 'Untitled Project.csv',
        'stage': 'modeling',
        'autopilotMode': autopilot_mode,
        'created': '2015-05-21T16:02:02.573565',
        'target': target,
        'metric': 'Gamma Deviance',
        'partition': {
            'cvMethod': 'random',
            'validationType': 'CV',
            'validationPct': None,
            'holdoutPct': 20,
            'reps': 5,
            'holdoutLevel': None,
            'validationLevel': None,
            'trainingLevel': None,
            'partitionKeyCols': None,
            'userPartitionCol': None,
            'cvHoldoutLevel': None,
            'datetimeCol': None
        },
        'recommender': {
            'isRecommender': False,
            'recommenderItemId': None,
            'recommenderUserId': None
        },
        'advancedOptions': {
            'weights': None,
            'blueprintThreshold': None,
            'responseCap': False,
            'seed': None,
            'smartDownsampled': False,
            'majorityDownsamplingRate': None,
            'offset': None,
            'exposure': None
        },
        'positiveClass': None,
        'maxTrainPct': 64,
        'holdoutUnlocked': True,
        'targetType': 'Regression'
    }


AIMED_PROJECT_JSON = json.dumps(construct_dummy_aimed_project())


def prep_successful_project_creation_responses(project=None):
    """
    Setup the responses library to mock calls to the API necessary to
    create a project

    Parameters
    ----------
    project : dict
        Project JSON as a dict, as would be expected from construct_dummy_aimed_project_json
    """
    if project is None:
        project = construct_dummy_aimed_project()

    pid = project.get('id')
    responses.add(responses.POST,
                  'https://host_name.com/projects/',
                  body='',
                  status=202,
                  content_type='application/json',
                  adding_headers={'Location': 'https://host_name.com/status/status-id/'}
                  )
    responses.add(responses.GET,
                  'https://host_name.com/status/status-id/',
                  status=303,
                  body='',
                  content_type='application/json',
                  adding_headers={
                      'Location': 'https://host_name.com/projects/{}/'.format(pid)}
                  )
    responses.add(responses.GET,
                  'https://host_name.com/projects/{}/'.format(pid),
                  status=200,
                  body=json.dumps(project),
                  content_type='application/json')


def prep_successful_aim_responses(project=None):
    """A helper to use with setting up test scenarios where the server is
    expected to successfully set the target.

    Parameters
    ----------
    project : dict
        Project JSON as a dict, as would be expected from construct_dummy_aimed_project_json
    """
    if project is None:
        project = construct_dummy_aimed_project()

    pid = project.get('id')
    project_url = 'https://host_name.com/projects/{}/'.format(pid)
    aim_url = project_url + 'aim/'

    responses.add(responses.PATCH,
                  aim_url,
                  body='',
                  status=202,
                  adding_headers={'Location': 'https://host_name.com/status/some-status/'},
                  content_type='application/json')

    responses.add(responses.GET,
                  'https://host_name.com/status/some-status/',
                  body='',
                  status=303,
                  adding_headers={'Location': project_url},
                  content_type='application/json')
    responses.add(responses.GET,
                  project_url,
                  body=json.dumps(project),
                  status=200,
                  content_type='application/json')

# TESTS ############################################################################################


def test_future_proof(project_with_target_data):
    Project.from_data(dict(project_with_target_data, future='new'))


@pytest.mark.usefixtures('known_warning')
def test_project_from_dict_is_deprecated(project_without_target_data):
    Project(project_without_target_data)


class ProjectTestCase(SDKTestcase):

    def test_instantiation_with_data(self):
        """
        Test instantiation Project(data)
        """
        data = {'id': 'project_id',
                'project_name': 'project_test_name',
                'mode': 2,
                'stage': 'stage',
                'target': 'test_target'}
        project_inst = Project.from_data(data)
        self.assertEqual(project_inst.id, data['id'])
        self.assertEqual(project_inst.project_name, data['project_name'])
        self.assertEqual(project_inst.mode, data['mode'])
        self.assertEqual(project_inst.stage, data['stage'])
        self.assertEqual(project_inst.target, data['target'])

        self.assertEqual(repr(project_inst), 'Project(project_test_name)')

    def test_print_project_nonascii_name(self):
        project = Project.from_data({'id': 'project-id',
                                     'project_name': u'\u3053\u3093\u306b\u3061\u306f'})
        print(project)

    def test_get_permalink(self):
        p = Project('pid')
        expected = 'https://host_name.com/projects/pid/models'
        self.assertEqual(expected, p.get_leaderboard_ui_permalink())

    @mock.patch('webbrowser.open')
    def test_open_leaderboard_browser(self, webbrowser_open):
        project = Project('p-id')
        project.open_leaderboard_browser()
        self.assertTrue(webbrowser_open.called)

    @responses.activate
    def test_create_project_async(self):
        prep_successful_project_creation_responses()

        new_project = Project.create(sourcedata='https://google.com')
        self.assertEqual(new_project.id, 'p-id')
        self.assertEqual(new_project.project_name, 'Untitled Project')

    @responses.activate
    def test_create_project_non_ascii_async(self):
        prep_successful_project_creation_responses()
        name = u'\xe3\x81\x82\xe3\x81\x82\xe3\x81\x82'
        Project.create("https://google.com", project_name=name)

    @responses.activate
    def test_get_project_metrics(self):
        """
        Test get project metrics
        """
        raw = """
        {"available_metrics":
            ["Gini Norm",
              "Weighted Gini Norm",
              "Weighted R Squared",
              "Weighted RMSLE",
              "Weighted MAPE",
              "Weighted Gamma Deviance",
              "Gamma Deviance",
              "RMSE",
              "Weighted MAD",
              "Tweedie Deviance",
              "MAD",
              "RMSLE",
              "Weighted Tweedie Deviance",
              "Weighted RMSE",
              "MAPE",
              "Weighted Poisson Deviance",
              "R Squared",
              "Poisson Deviance"],
         "feature_name": "SalePrice"}
        """
        expected_url = 'https://host_name.com/projects/p-id/features/metrics/'
        responses.add(responses.GET,
                      expected_url,
                      body=raw,
                      status=200,
                      content_type='application/json')
        get_project = Project('p-id').get_metrics('SalePrice')
        self.assertEqual(responses.calls[0].request.url,
                         expected_url + '?featureName=SalePrice')
        self.assertEqual(get_project["feature_name"], 'SalePrice')

    @responses.activate
    def test_get_project(self):
        """
        Test get project
        """
        responses.add(responses.GET,
                      'https://host_name.com/projects/p-id/',
                      body=AIMED_PROJECT_JSON,
                      status=200,
                      content_type='application/json')
        get_project = Project.get('p-id')
        self.assertEqual(get_project.id, 'p-id')
        self.assertEqual(get_project.project_name, 'Untitled Project')
        self.assertEqual(get_project.target, 'SalePrice')
        self.assertEqual(get_project.target_type, 'Regression')
        self.assertEqual(get_project.stage, 'modeling')
        self.assertEqual(get_project.metric, 'Gamma Deviance')
        self.assertIsNone(get_project.positive_class)
        self.assertEqual(get_project.max_train_pct, 64)
        self.assertTrue(get_project.holdout_unlocked)
        self.assertIsInstance(get_project.partition, dict)
        self.assertIsInstance(get_project.recommender, dict)
        self.assertIsInstance(get_project.advanced_options, dict)
        self.assertNotIn('weights', get_project.advanced_options)
        self.assertNotIn('offset', get_project.advanced_options)
        self.assertNotIn('exposure', get_project.advanced_options)

        self.assertIsInstance(get_project.created, datetime.datetime)

        assert get_project.partition['cv_method'] == 'random'

    @responses.activate
    def test_get_project_weights_offset_exposure(self):
        """
        Test get project with a weights, offset and exposure columns
        """
        # given a project with a weights column
        pid = '582e4309100d2b13b939b223'
        weight_var = 'weight_variable'
        offset_var = ['offset_variable']
        exposure_var = 'exposure_variable'
        project_data = construct_dummy_aimed_project()
        project_data['advancedOptions']['weights'] = weight_var
        project_data['advancedOptions']['offset'] = offset_var
        project_data['advancedOptions']['exposure'] = exposure_var
        # and a mocked API GET /projects/<pid>/ response
        responses.add(responses.GET,
                      'https://host_name.com/projects/{}/'.format(pid),
                      body=json.dumps(project_data),
                      status=200,
                      content_type='application/json')

        # when method Project.get is called
        project = Project.get(pid)

        # then the resulting object contains weights in advanced options
        assert project.advanced_options['weights'] == weight_var
        assert project.advanced_options['offset'] == offset_var
        assert project.advanced_options['exposure'] == exposure_var

    @responses.activate
    def test_delete_project(self):
        """
        Test delete project
        """
        responses.add(responses.DELETE,
                      'https://host_name.com/projects/p-id/',
                      status=204)

        project = Project('p-id')
        del_result = project.delete()
        self.assertEqual(responses.calls[0].request.method, 'DELETE')
        self.assertIsNone(del_result)

    @patch('os.path.isfile')
    def test_non_ascii_filename(self, isfile_mock):
        isfile_mock.return_value = True
        bad_filename = u'\xc3\x98.csv'
        with pytest.raises(errors.IllegalFileName):
            Project.create(bad_filename)

    @responses.activate
    def test_create_non_ascii_filepath_is_okay(self):
        """As long as the file name is ascii, we're good"""
        prep_successful_project_creation_responses()
        path = fixture_file_path(u'日本/synthetic-100.csv')

        Project.create(path)
        # decoded to str implicitly
        self.assertEqual(
            responses.calls[0].request.url,
            'https://host_name.com/projects/')
        request_message = responses.calls[0].request.body
        with open(path, 'rb') as fd:
            self.assertIn(fd.read(), request_message.to_string())

    @responses.activate
    def test_rename(self):
        responses.add(responses.PATCH,
                      'https://host_name.com/projects/p-id/',
                      body='',
                      status=200,
                      content_type='application/json')
        project = Project('p-id')
        project.rename('new name')
        assert responses.calls[0].request.method == 'PATCH'
        payload = json.loads(responses.calls[0].request.body)
        assert project.project_name == payload['projectName'] == 'new name'

    @responses.activate
    def test_unlock_holdout(self):
        responses.add(responses.PATCH,
                      'https://host_name.com/projects/p-id/',
                      body='',
                      status=200,
                      content_type='application/json')
        project = Project('p-id')
        upd_data = project.unlock_holdout()
        self.assertEqual(responses.calls[0].request.method, 'PATCH')
        payload = json.loads(responses.calls[0].request.body)
        self.assertTrue(payload['holdoutUnlocked'])
        self.assertTrue(upd_data)

    @responses.activate
    def test_set_worker_count(self):
        responses.add(responses.PATCH,
                      'https://host_name.com/projects/p-id/',
                      body='',
                      status=200,
                      content_type='application/json')
        project = Project('p-id')
        project.set_worker_count(20)
        self.assertEqual(responses.calls[0].request.method, 'PATCH')
        payload = json.loads(responses.calls[0].request.body)
        self.assertTrue(payload['workerCount'])

    @responses.activate
    def test_project_create_uses_read_timeout(self):
        """
        Check that the read_timeout parameter gets passed correctly down into
        the `requests` library

        The 400 is just because it's a simple way to short-circuit out of the project
        creation flow, which uses 3 total requests.
        """
        path = fixture_file_path('synthetic-100.csv')

        responses.add(responses.POST,
                      'https://host_name.com/projects/',
                      body='',
                      status=400
                      )
        with mock.patch.object(Project._client, 'request',
                               wraps=Project._client.request) as mock_request:
            try:
                Project.create(path, read_timeout=2)
            except errors.ClientError:
                pass

            timeout = mock_request.call_args[1]['timeout']
            assert timeout[0] == 6.05  # Connect timeout; specified in RESTClientObject
            assert timeout[1] == 2  # Read timeout; specified in the function call

    @responses.activate
    def test_by_upload_file_path(self):
        """
        Project.create(
            'synthetic-100.csv')
        """
        prep_successful_project_creation_responses()
        path = fixture_file_path('synthetic-100.csv')

        Project.create(path)
        # decoded to str implicitly
        self.assertEqual(
            responses.calls[0].request.url,
            'https://host_name.com/projects/')
        request_message = responses.calls[0].request.body
        with open(path, 'rb') as fd:
            self.assertIn(fd.read(), request_message.to_string())

    def test_by_upload_file_path_fail(self):
        """
        Bad file name: Project.create('meh.csv')
        """
        path = fixture_file_path('does_not_exist.csv')
        with self.assertRaises(errors.InputNotUnderstoodError):
            Project.create(path)

    @responses.activate
    def test_by_upload_file_content(self):
        """
        Project.create(b'lalalala')
        """
        prep_successful_project_creation_responses()

        content_line = six.b('one,two\n' + '1,2'*100)
        Project.create(content_line)
        # decoded to str implicitly
        request_message = responses.calls[0].request.body
        self.assertIn(content_line, request_message.to_string())

    def test_by_upload_content_encoding(self):
        """
        Bad content encoding Project.create(u'lalalala')
        """
        content_line = u'lalalala'
        with self.assertRaises(errors.InputNotUnderstoodError):
            Project.create(content_line)

    @responses.activate
    def test_by_upload_from_fd(self):
        """
        Project.create(
          sourcedata=open('synthetic-100.csv'))
        """
        prep_successful_project_creation_responses()

        path = fixture_file_path('synthetic-100.csv')

        with open(path, 'rb') as fd:
            Project.create(sourcedata=fd)
            request_message = responses.calls[0].request.body

            with open(path, 'rb') as fd2:
                self.assertIn(fd2.read(), request_message.to_string())

        file_like = six.StringIO('thra\ntata\nrata')
        Project.create(
            sourcedata=file_like)

        # decoded to str implicitly
        request_message = responses.calls[3].request.body
        self.assertIn(six.b('thra\ntata\nrata'), request_message.to_string())

    @responses.activate
    def test_by_upload_file_seek(self):
        """
        Seek to EOF Project.create(
            open('synthetic-100.csv')
        """
        prep_successful_project_creation_responses()

        path = fixture_file_path('synthetic-100.csv')
        with open(path, 'rb') as fd:
            fd.seek(20000000)
            Project.create(fd)
            # decoded to str implicitly

            request_message = responses.calls[0].request.body
            with open(path, 'rb') as fd2:
                self.assertIn(fd2.read(), request_message.to_string())

    @responses.activate
    def test_by_upload_file_closed(self):
        """
        Closed fd Project.create(
            open('synthetic-100.csv')
        """
        path = fixture_file_path('synthetic-100.csv')
        responses.add(responses.POST,
                      'https://host_name.com/projects/p-id/upload/',
                      body='',
                      status=200,
                      )
        fd = open(path)
        fd.close()
        with self.assertRaises(ValueError):
            Project.create(fd)

    @responses.activate
    def test_upload_by_file_url(self):
        """
        Project.create('http:/google.com/datarobot.csv')
        """
        prep_successful_project_creation_responses()

        link = 'http:/google.com/datarobot.csv'
        Project.create(sourcedata=link)
        request_message = responses.calls[0].request.body
        assertJsonEq(
            request_message,
            json.dumps(
                {"url": link, "projectName": "Untitled Project"}
            )
        )
        self.assertEqual(
            responses.calls[0].request.url,
            'https://host_name.com/projects/')

    @responses.activate
    def test_set_target(self):
        """
        Project('p-id').set_target('SalePrice', metric='RMSE')
        """
        prep_successful_aim_responses()
        opts = AdvancedOptions(weights='WeightName',
                               offset=['OffsetName1', 'OffsetName2'],
                               exposure='ExposureName')
        upd_project = Project('p-id').set_target(
            'SalePrice',
            metric='RMSE',
            advanced_options=opts)

        request_message = responses.calls[0].request.body
        assertJsonEq(request_message, json.dumps({
            'target': 'SalePrice',
            'mode': AUTOPILOT_MODE.FULL_AUTO,
            'metric': 'RMSE',
            'weights': 'WeightName',
            'offset': ['OffsetName1', 'OffsetName2'],
            'exposure': 'ExposureName',
            'smartDownsampled': False
        }))
        self.assertEqual(responses.calls[0].request.method, 'PATCH')
        self.assertEqual(responses.calls[1].request.method, 'GET')
        self.assertIsInstance(upd_project, Project)
        advanced = upd_project.advanced_options
        assert advanced['response_cap'] is False
        assert advanced['smart_downsampled'] is False

    @responses.activate
    def test_set_target_price(self):
        """
        Project('p-id').set_target('SalePrice', metric='RMSE')
        """
        prep_successful_aim_responses()
        upd_project = Project('p-id').set_target('SalePrice')

        request_message = responses.calls[0].request.body
        assertJsonEq(request_message, json.dumps({
            'target': 'SalePrice',
            'mode': AUTOPILOT_MODE.FULL_AUTO,
        }))
        self.assertEqual(upd_project.metric, 'Gamma Deviance')

    @responses.activate
    def test_set_target_quickrun_mode(self):
        prep_successful_aim_responses()
        Project('p-id').set_target('SalePrice', mode=AUTOPILOT_MODE.QUICK)

        request_body = json.loads(responses.calls[0].request.body)
        assert request_body['mode'] == AUTOPILOT_MODE.FULL_AUTO
        assert request_body['quickrun'] is True

    @responses.activate
    def test_set_target_async_error(self):
        """
        Project('p-id').set_target('SalePrice', metric='RMSE')
        """
        responses.add(responses.PATCH,
                      'https://host_name.com/projects/p-id/aim/',
                      body='',
                      status=202,
                      adding_headers={'Location': 'https://host_name.com/projects/p-id/'},
                      content_type='application/json')

        responses.add(responses.GET,
                      'https://host_name.com/projects/p-id/',
                      body=json.dumps({'status': 'ERROR'}),
                      status=200,
                      content_type='application/json')
        with self.assertRaises(errors.AsyncProcessUnsuccessfulError):
            Project('p-id').set_target(
                'SalePrice',
                metric='RMSE',
            )
        self.assertEqual(responses.calls[0].request.method, 'PATCH')
        self.assertEqual(responses.calls[1].request.method, 'GET')

    def test_advanced_options_must_be_object(self):
        with self.assertRaises(TypeError):
            Project('p-id').set_target(
                'SalePrice',
                advanced_options={'garbage': 'in'}
            )

    @responses.activate
    def test_set_blueprint_threshold(self):
        """
        Set blueprint threshold
        """
        prep_successful_aim_responses()

        opts = AdvancedOptions(blueprint_threshold=2)
        upd_project = Project('p-id').set_target(
            'SalePrice',
            advanced_options=opts)

        request_message = responses.calls[0].request.body
        assertJsonEq(request_message, json.dumps({
            'target': 'SalePrice',
            'mode': AUTOPILOT_MODE.FULL_AUTO,
            'blueprintThreshold': 2,
            'smartDownsampled': False
        }))
        self.assertEqual(responses.calls[0].request.method, 'PATCH')
        self.assertEqual(responses.calls[1].request.method, 'GET')
        self.assertIsInstance(upd_project, Project)

    @responses.activate
    def test_set_response_cap(self):
        """
        Set Response Cap
        """
        prep_successful_aim_responses()

        opts = AdvancedOptions(response_cap=0.7)
        upd_project = Project('p-id').set_target(
            'SalePrice',
            advanced_options=opts)

        request_message = responses.calls[0].request.body
        assertJsonEq(request_message, json.dumps({
            'target': 'SalePrice',
            'mode': AUTOPILOT_MODE.FULL_AUTO,
            'responseCap': 0.7,
            'smartDownsampled': False
        }))
        self.assertEqual(responses.calls[0].request.method, 'PATCH')
        self.assertEqual(responses.calls[1].request.method, 'GET')
        self.assertIsInstance(upd_project, Project)

    @responses.activate
    def test_set_seed(self):
        """
        Set Response Cap
        """
        prep_successful_aim_responses()

        opts = AdvancedOptions(seed=22)
        upd_project = Project('p-id').set_target(
            'SalePrice',
            advanced_options=opts)

        request_message = responses.calls[0].request.body
        assertJsonEq(request_message, json.dumps({
            'target': 'SalePrice',
            'mode': AUTOPILOT_MODE.FULL_AUTO,
            'seed': 22,
            'smartDownsampled': False
        }))
        self.assertEqual(responses.calls[0].request.method, 'PATCH')
        self.assertEqual(responses.calls[1].request.method, 'GET')
        self.assertIsInstance(upd_project, Project)

    @responses.activate
    def test_set_smart_sampled(self):
        prep_successful_aim_responses()

        opts = AdvancedOptions(smart_downsampled=True, majority_downsampling_rate=50.5)
        upd_project = Project('p-id').set_target('SalePrice', advanced_options=opts)

        request_message = responses.calls[0].request.body
        expected_message = {'target': 'SalePrice', 'mode': AUTOPILOT_MODE.FULL_AUTO,
                            'smartDownsampled': True, 'majorityDownsamplingRate': 50.5}

        assertJsonEq(request_message, json.dumps(expected_message))
        assert isinstance(upd_project, Project)

    @responses.activate
    def test_set_target_advance_partition_method_cv(self):
        """
        Set project with advanced partition method
        """
        prep_successful_aim_responses()

        part_method = UserCV(user_partition_col='NumPartitions',
                             cv_holdout_level=1, seed=42)
        p = Project('p-id').set_target(
            'SalePrice',
            partitioning_method=part_method)
        request_message = responses.calls[0].request.body
        assertJsonEq(request_message, json.dumps({
            'target': 'SalePrice',
            'mode': AUTOPILOT_MODE.FULL_AUTO,
            'userPartitionCol': 'NumPartitions',
            'cvHoldoutLevel': 1,
            'seed': 42,
            'validationType': 'user',
            'cvMethod': 'CV'
        }))
        self.assertEqual(responses.calls[0].request.method, 'PATCH')
        self.assertEqual(responses.calls[1].request.method, 'GET')
        self.assertIsInstance(p, Project)

    @responses.activate
    def test_set_target_advance_partition_method_tvh(self):
        """
        Set project with advanced partition method
        """
        prep_successful_aim_responses()
        part_method = UserTVH(user_partition_col='NumPartitions',
                              validation_level=1, training_level=2,
                              holdout_level=3,
                              seed=42)
        p = Project('p-id').set_target(
            'SalePrice',
            partitioning_method=part_method)
        request_message = responses.calls[0].request.body
        assertJsonEq(request_message, json.dumps({
            'target': 'SalePrice',
            'mode': AUTOPILOT_MODE.FULL_AUTO,
            'userPartitionCol': 'NumPartitions',
            'holdoutLevel': 3,
            'seed': 42,
            'validationLevel': 1,
            'trainingLevel': 2,
            'validationType': 'TVH',
            'cvMethod': 'user'
        }))
        self.assertEqual(responses.calls[0].request.method, 'PATCH')
        self.assertEqual(responses.calls[1].request.method, 'GET')
        self.assertIsInstance(p, Project)

    @responses.activate
    def test_set_target_specify_positive_class(self):
        """
        Set project with advanced partition method
        """
        prep_successful_aim_responses()

        p = Project('p-id').set_target(
            'Forks',
            positive_class='None or Unspecified')
        request_message = responses.calls[0].request.body
        assertJsonEq(request_message, json.dumps({
            'target': 'Forks',
            'positiveClass': 'None or Unspecified',
            'mode': AUTOPILOT_MODE.FULL_AUTO
        }))
        self.assertEqual(responses.calls[0].request.method, 'PATCH')
        self.assertEqual(responses.calls[1].request.method, 'GET')
        self.assertIsInstance(p, Project)

    @responses.activate
    @pytest.mark.usefixtures('known_warning')
    def test_set_target_quickrun_param(self):
        """
        Set project with quickrun option
        """
        prep_successful_aim_responses()

        p = Project('p-id').set_target(
            'Forks', mode=AUTOPILOT_MODE.MANUAL,
            quickrun=True)
        request_message = responses.calls[0].request.body
        assertJsonEq(request_message, json.dumps({
            'target': 'Forks',
            'quickrun': True,
            'mode': AUTOPILOT_MODE.FULL_AUTO
        }))
        self.assertEqual(responses.calls[0].request.method, 'PATCH')
        self.assertEqual(responses.calls[1].request.method, 'GET')
        self.assertIsInstance(p, Project)

    @responses.activate
    @pytest.mark.usefixtures('known_warning')
    def test_set_target_semi_auto_deprecated(self):
        """
        Set project with quickrun option
        """
        prep_successful_aim_responses()
        Project('p-id').set_target('Forks', mode=AUTOPILOT_MODE.SEMI_AUTO)

    def test_pass_advance_part_wrong(self):
        with self.assertRaises(TypeError):
            Project('p-id').set_target(
                'SalePrice',
                partitioning_method={'CV': 'TVH'})

    @responses.activate
    def test_pause_autopilot(self):
        """
        Project('p-id').pause_autopilot()
        """
        responses.add(responses.POST,
                      'https://host_name.com/projects/p-id/autopilot/',
                      body='',
                      status=202,
                      content_type='application/json')
        self.assertTrue(Project('p-id').pause_autopilot())
        request_message = responses.calls[0].request.body
        assertJsonEq(request_message, json.dumps({
            'command': 'stop'
        }))

    @responses.activate
    def test_unpause_autopilot(self):
        """
        Project('p-id').unpause_autopilot()
        """
        responses.add(responses.POST,
                      'https://host_name.com/projects/p-id/autopilot/',
                      body='',
                      status=202,
                      content_type='application/json')
        self.assertTrue(Project('p-id').unpause_autopilot())
        request_message = responses.calls[0].request.body
        assertJsonEq(request_message, json.dumps({
            'command': 'start',
        }))

    @responses.activate
    def test_start_autopilot(self):
        """
        Project('p-id').start_autopilot('featurelist-id')
        """
        responses.add(responses.POST,
                      'https://host_name.com/projects/p-id/autopilots/',
                      body='',
                      status=201,
                      content_type='application/json')
        Project('p-id').start_autopilot('featurelist-id')
        request_message = responses.calls[0].request.body
        assertJsonEq(request_message, json.dumps({
            'featurelistId': 'featurelist-id',
            'mode': AUTOPILOT_MODE.FULL_AUTO
        }))

    @responses.activate
    @pytest.mark.usefixtures('known_warning')
    def test_start_autopilot_semi_auto_deprecated(self):
        """
        Project('p-id').start_autopilot('featurelist-id')
        """
        responses.add(responses.POST,
                      'https://host_name.com/projects/p-id/autopilots/',
                      body='',
                      status=201,
                      content_type='application/json')
        Project('p-id').start_autopilot('featurelist-id', mode=AUTOPILOT_MODE.SEMI_AUTO)

    @responses.activate
    def test_get_featurelists(self):
        """project.get_featurelists()

        """
        some_featurelists = [
            {'id': 'f-id-1',
             'projectId': 'p-id',
             'name': 'Raw Features',
             'features': ['One Fish', 'Two Fish', 'Red Fish', 'Blue Fish']},
            {'id': 'f-id-2',
             'projectId': 'p-id',
             'name': 'Informative Features',
             'features': ['One Fish', 'Red Fish', 'Blue Fish']},
            {'id': 'f-id-3',
             'projectId': 'p-id',
             'name': 'Custom Features',
             'features': ['One Fish', 'Blue Fish']},
        ]

        responses.add(responses.GET,
                      'https://host_name.com/projects/p-id/featurelists/',
                      body=json.dumps(some_featurelists),
                      status=200,
                      content_type='application/json')
        flists = Project('p-id').get_featurelists()
        for flist in flists:
            self.assertIsInstance(flist, Featurelist)

    @responses.activate
    def test_create_featurelist(self):
        """Project.create_featurelist(name='Featurelist Name',
                                      features=list_of_features)

        """
        project = Project('p-id')
        name = 'Featurelist name'
        features = ['One Fish', 'Two Fish', 'Blue Fish']

        responses.add(responses.POST,
                      'https://host_name.com/projects/p-id/featurelists/',
                      body='',
                      status=201,
                      content_type='application/json',
                      adding_headers={
                          'Location': 'https://host_name.com/projects/p-id/featurelists/f-id-new/'
                      })
        new_flist = project.create_featurelist(name, features)
        self.assertEqual(new_flist.name, name)
        self.assertEqual(new_flist.features, features)
        self.assertEqual(new_flist.project_id, 'p-id')

    def test_create_featurelist_duplicate_features(self):
        project = Project('p-id')
        with pytest.raises(errors.DuplicateFeaturesError) as exc_info:
            project.create_featurelist('test', ['feature', 'feature'])
        assert_raised_regex(exc_info, 'Can\'t create featurelist with duplicate features')

    @responses.activate
    def test_start_project(self):
        """
        Project.start("test_name",
                      "file.csv",
                      "a_target",
                      worker_count=4,
                      metric="a_metric")
        """
        path = fixture_file_path('synthetic-100.csv')
        prep_successful_project_creation_responses()

        responses.add(responses.PATCH,
                      'https://host_name.com/projects/p-id/',
                      body='',
                      status=200,
                      content_type='application/json')

        prep_successful_aim_responses()

        proj = Project.start(project_name="test_name",
                             sourcedata=path,
                             target="a_target",
                             worker_count=4,
                             metric="a_metric")
        self.assert_project_start_call_order()
        self.assertIsInstance(proj, Project)

    @responses.activate
    def test_start_project_from_dataframe(self):
        """
        Project.start("test_name",
                      "file.csv",
                      "a_target",
                      worker_count=4,
                      metric="a_metric")
        """
        prep_successful_project_creation_responses()

        responses.add(responses.PATCH,
                      'https://host_name.com/projects/p-id/',
                      body='',
                      status=200,
                      content_type='application/json')

        prep_successful_aim_responses()

        dataframe = pd.DataFrame({'a_target': range(100),
                                  'predictor': range(100, 200)})
        proj = Project.start(dataframe,
                             "a_target",
                             "test_name",
                             worker_count=4,
                             metric="a_metric")
        self.assert_project_start_call_order()
        self.assertIsInstance(proj, Project)

    @responses.activate
    def test_start_project_in_manual_mode(self):
        """
        Project.start("test_name",
                      "file.csv",
                      "a_target",
                      worker_count=4,
                      metric="a_metric",
                      autopilot_on=False)
        """
        path = fixture_file_path('synthetic-100.csv')
        prep_successful_project_creation_responses()
        responses.add(responses.PATCH,
                      'https://host_name.com/projects/p-id/',
                      body='',
                      status=200,
                      content_type='application/json')
        prep_successful_aim_responses()

        proj = Project.start(path,
                             "test_name",
                             "a_target",
                             worker_count=4,
                             metric="a_metric",
                             autopilot_on=False)
        self.assert_project_start_call_order()
        self.assertIsInstance(proj, Project)

        req_body = json.loads(responses.calls[4].request.body)
        self.assertEqual(req_body['mode'], AUTOPILOT_MODE.MANUAL)

    def assert_project_start_call_order(self):
        """Run this assertion to assert that the expected calls for project.start
        happened, and in the correct order

        This is a terribly brittle test. If we can come up with something
        better, let's go with that.
        """
        # Create Project
        self.assertEqual(responses.calls[0].request.url,
                         'https://host_name.com/projects/')
        self.assertEqual(responses.calls[0].request.method, 'POST')

        # Get Project Creation Status
        self.assertEqual(responses.calls[1].request.url,
                         'https://host_name.com/status/status-id/')
        self.assertEqual(responses.calls[1].request.method, 'GET')

        # Get Created Project
        self.assertEqual(responses.calls[2].request.url,
                         'https://host_name.com/projects/p-id/')
        self.assertEqual(responses.calls[2].request.method, 'GET')

        # Set Worker Count
        self.assertEqual(responses.calls[3].request.url,
                         'https://host_name.com/projects/p-id/')
        self.assertEqual(responses.calls[3].request.method, 'PATCH')

        # Set Target
        self.assertEqual(responses.calls[4].request.url,
                         'https://host_name.com/projects/p-id/aim/')
        self.assertEqual(responses.calls[4].request.method, 'PATCH')

        # Get Status of Finalizing Project
        self.assertEqual(responses.calls[5].request.url,
                         'https://host_name.com/status/some-status/')
        self.assertEqual(responses.calls[5].request.method, 'GET')

        # Get Finalized Project
        self.assertEqual(responses.calls[6].request.url,
                         'https://host_name.com/projects/p-id/')
        self.assertEqual(responses.calls[6].request.method, 'GET')

    @responses.activate
    def test_set_target_featurelist(self):
        """
        proj.set_target('test_target', featurelist_id=...)
        """
        prep_successful_aim_responses()
        Project('p-id').set_target('a_target', featurelist_id='f-id-3')
        body = json.loads(responses.calls[0].request.body)
        assert body['featurelistId'] == 'f-id-3'

    @responses.activate
    def test_attach_file_with_link_goes_to_url(self):
        """
        Project.create('https://google.com/file.csv')
        """
        prep_successful_project_creation_responses()

        link = 'http:/google.com/datarobot.csv'
        Project.create(link)
        request_message = responses.calls[0].request.body
        assertJsonEq(request_message, json.dumps({"url": link, "projectName": "Untitled Project"}))
        self.assertEqual(
            responses.calls[0].request.url,
            'https://host_name.com/projects/')

    @responses.activate
    def test_attach_file_with_file_path(self):
        """
        Project.create('synthetic-100.csv')
        """
        prep_successful_project_creation_responses()

        path = fixture_file_path('synthetic-100.csv')
        Project.create(path)

        self.assertEqual(
            responses.calls[0].request.url,
            'https://host_name.com/projects/')
        request_message = responses.calls[0].request.body
        with open(path, 'rb') as fd:
            self.assertIn(fd.read(), request_message.read())

    @responses.activate
    def test_attach_file_with_non_csv_file_path(self):
        """
        Project.create('dataset.xlsx')
        """
        prep_successful_project_creation_responses()

        path = fixture_file_path('onehundredrows.xlsx')
        Project.create(path)
        self.assertEqual(
            responses.calls[0].request.url,
            'https://host_name.com/projects/')
        request_message = responses.calls[0].request.body.read()
        with open(path, 'rb') as fd:
            self.assertIn(fd.read(), request_message)
        fname = re.search(b'filename="(.*)"',
                          request_message).group(1)
        self.assertEqual(fname, b'onehundredrows.xlsx')

    @responses.activate
    def test_get_status_underscorizes(self):
        body = json.dumps({'autopilotDone': True,
                           'stage': 'modeling',
                           'stageDescription': 'Ready for modeling'})
        responses.add(responses.GET,
                      'https://host_name.com/projects/p-id/status/',
                      status=200,
                      body=body,
                      content_type='application/json'
                      )
        status = Project('p-id').get_status()
        self.assertEqual(status['stage'], 'modeling')
        self.assertTrue(status['autopilot_done'])

    @responses.activate
    def test_get_blueprints(self):
        body = json.dumps([
            {"projectId": "p-id",
             "processes": [
                 "Regularized Linear Model Preprocessing v5",
                 "Log Transformed Response"
             ],
             "id": "cbb4d6101dea1768ed79d75edd84c6c7",
             "modelType": "Auto-tuned K-Nearest Neighbors Regressor (Minkowski Distance)"
             },
            {"projectId": "p-id",
             "processes": [
                 "Regularized Linear Model Preprocessing v12",
                 "Log Transformed Response"
             ],
             "id": "e0708bd47f9fd21019a5ab7846e8364d",
             "modelType": "Auto-tuned Stochastic Gradient Descent Regression"
             }])
        responses.add(responses.GET,
                      'https://host_name.com/projects/p-id/blueprints/',
                      status=200,
                      body=body,
                      content_type='application/json'
                      )
        menu = Project('p-id').get_blueprints()
        for item in menu:
            self.assertIsInstance(item, Blueprint)
            self.assertEqual(item.project_id, 'p-id')
        bluepr1 = menu[0]
        bluepr2 = menu[1]
        self.assertIsInstance(bluepr1.processes, list)
        self.assertEqual(bluepr1.processes[0],
                         'Regularized Linear Model Preprocessing v5')
        self.assertEqual(bluepr1.processes[1], 'Log Transformed Response')
        self.assertEqual(bluepr1.model_type,
                         'Auto-tuned K-Nearest Neighbors Regressor (Minkowski Distance)')
        self.assertIsInstance(bluepr2.processes, list)
        self.assertEqual(bluepr2.processes[0],
                         'Regularized Linear Model Preprocessing v12')
        self.assertEqual(bluepr2.processes[1],
                         'Log Transformed Response')
        self.assertEqual(bluepr2.model_type,
                         'Auto-tuned Stochastic Gradient Descent Regression')


class TestProjectJobListing(SDKTestcase):

    job1_queued_dict = {
                'status': 'queue',
                'processes': [
                    'Majority Class Classifier'
                ],
                'projectId': '556902e8100d2b3728d47551',
                'samplePct': 32.0,
                'modelType': 'Majority Class Classifier',
                'featurelistId': '556902eb100d2b37d1130771',
                'blueprintId': '89e08076a908e859c07af49bd4aa6a0f',
                'id': '10',
                'modelId': '556902ef100d2b37da13077c'
            }
    job2_queued_dict = {
                'status': 'queue',
                'processes': [
                    'One-Hot Encoding',
                    'Missing Values Imputed',
                    'RuleFit Classifier'
                ],
                'projectId': '556902e8100d2b3728d47551',
                'samplePct': 32.0,
                'modelType': 'RuleFit Classifier',
                'featurelistId': '556902eb100d2b37d1130771',
                'blueprintId': 'a8959bc1d46f07fb3dc14db7c1e3fc99',
                'id': '11',
                'modelId': '556902ef100d2b37da13077d'
            }
    job3_queued_dict = {
                'status': 'queue',
                'processes': [
                    'One-Hot Encoding',
                    'Missing Values Imputed',
                    'RuleFit Classifier'
                ],
                'projectId': '556902e8100d2b3728d47551',
                'samplePct': 64.0,
                'modelType': 'RuleFit Classifier',
                'featurelistId': '556902eb100d2b37d1130771',
                'blueprintId': 'a8959bc1d46f07fb3dc14db7c1e3fc99',
                'id': '17',
                'modelId': '556902ef100d2b37da13077d'
            }
    job1_inprogress_dict = dict(job1_queued_dict, status='inprogress')
    job2_inprogress_dict = dict(job2_queued_dict, status='inprogress')

    predict_job_queued_dict = {
        'status': 'queue',
        'projectId': '56b62892ccf94e7e939c89c8',
        'message': '',
        'id': '27',
        'modelId': '56b628b7ccf94e0444bb8152'
    }

    predict_job_errored_dict = {
        'status': 'error',
        'projectId': '56b62892ccf94e7e939c89c8',
        'message': '',
        'id': '23',
        'modelId': '56b628b7ccf94e0444bb8152'
    }

    all_jobs_response = {
        'count': 4,
        'next': None,
        'jobs': [
            {
                'status': 'inprogress',
                'url': 'https://host_name.com/projects/p-id/modelJobs/1/',
                'id': '1',
                'jobType': 'model',
                'projectId': 'p-id'
            },
            {
                'status': 'inprogress',
                'url': 'https://host_name.com/projects/p-id/modelJobs/2/',
                'id': '2',
                'jobType': 'model',
                'projectId': 'p-id'
            },
            {
                'status': 'queue',
                'url': 'https://host_name.com/projects/p-id/predictJobs/3/',
                'id': '3',
                'jobType': 'predict',
                'projectId': 'p-id'
            },
            {
                'status': 'queue',
                'url': 'https://host_name.com/projects/p-id/modelJobs/4/',
                'id': '4',
                'jobType': 'model',
                'projectId': 'p-id'
            }
        ],
        'previous': None
    }

    all_error_jobs_response = {
        'count': 1,
        'next': None,
        'jobs': [
            {
                'status': 'error',
                'url': 'https://host_name.com/projects/p-id/predictJobs/3/',
                'id': '3',
                'jobType': 'predict',
                'projectId': 'p-id'
            }
        ],
        'previous': None
    }

    @responses.activate
    def test_get_all_jobs(self):
        body = json.dumps(self.all_jobs_response)
        responses.add(responses.GET,
                      'https://host_name.com/projects/p-id/jobs/',
                      status=200,
                      body=body,
                      content_type='application/json'
                      )
        jobs = Project('p-id').get_all_jobs()
        self.assertEqual(len(jobs), 4)

    @responses.activate
    def test_get_all_errored_jobs(self):
        body = json.dumps(self.all_error_jobs_response)
        responses.add(responses.GET,
                      'https://host_name.com/projects/p-id/jobs/',
                      status=200,
                      body=body,
                      content_type='application/json'
                      )
        jobs = Project('p-id').get_all_jobs(status=QUEUE_STATUS.ERROR)
        self.assertEqual(responses.calls[0].request.url,
                         'https://host_name.com/projects/p-id/jobs/?status=error')
        self.assertEqual(len(jobs), 1)

    @responses.activate
    def test_get_model_jobs(self):
        job_dict = self.job1_queued_dict
        body = json.dumps([job_dict])
        responses.add(responses.GET,
                      'https://host_name.com/projects/p-id/modelJobs/',
                      status=200,
                      body=body,
                      content_type='application/json'
                      )
        jobs = Project('p-id').get_model_jobs(status=QUEUE_STATUS.QUEUE)
        self.assertEqual(
            responses.calls[0].request.url,
            'https://host_name.com/projects/p-id/modelJobs/?status=queue')
        self.assertEqual(len(jobs), 1)
        self.assertDictEqual(jobs[0].__dict__, ModelJob(job_dict).__dict__)

    @responses.activate
    def test_get_model_jobs_requests_all_by_default(self):
        job_dict = self.job1_queued_dict
        body = json.dumps([job_dict])
        responses.add(responses.GET,
                      'https://host_name.com/projects/p-id/modelJobs/',
                      status=200,
                      body=body,
                      content_type='application/json'
                      )
        jobs = Project('p-id').get_model_jobs()
        self.assertEqual(
            responses.calls[0].request.url,
            'https://host_name.com/projects/p-id/modelJobs/')
        self.assertEqual(len(jobs), 1)
        self.assertDictEqual(jobs[0].__dict__, ModelJob(job_dict).__dict__)

    @responses.activate
    def test_get_predict_jobs(self):
        body = json.dumps([self.predict_job_errored_dict])
        responses.add(responses.GET,
                      'https://host_name.com/projects/p-id/predictJobs/',
                      status=200,
                      body=body,
                      content_type='application/json')
        jobs = Project('p-id').get_predict_jobs(status=QUEUE_STATUS.ERROR)
        self.assertEqual(responses.calls[0].request.url,
                         'https://host_name.com/projects/p-id/predictJobs/?status=error')
        self.assertEqual(len(jobs), 1)
        result_job = jobs[0]
        expected_job = PredictJob(self.predict_job_errored_dict)
        self.assertEqual(expected_job.id, result_job.id)
        self.assertEqual(expected_job.project, result_job.project)

    @responses.activate
    def test_get_predict_jobs_default(self):
        body = json.dumps([self.predict_job_queued_dict])
        responses.add(responses.GET,
                      'https://host_name.com/projects/p-id/predictJobs/',
                      status=200,
                      body=body,
                      content_type='application/json')
        jobs = Project('p-id').get_predict_jobs()
        self.assertEqual(responses.calls[0].request.url,
                         'https://host_name.com/projects/p-id/predictJobs/')
        self.assertEqual(len(jobs), 1)
        result_job = jobs[0]
        expected_job = PredictJob(self.predict_job_queued_dict)
        self.assertEqual(expected_job.id, result_job.id)
        self.assertEqual(expected_job.project, result_job.project)

    @patch('datarobot.Project.get_model_jobs')
    def test_job_status_counter(self, mock_get_jobs):
        project = Project('p-id')
        jobs0 = []
        jobs1 = [ModelJob(self.job1_queued_dict)]
        jobs2 = [ModelJob(self.job1_inprogress_dict), ModelJob(self.job2_queued_dict)]
        jobs3 = [ModelJob(self.job2_inprogress_dict)]
        mock_get_jobs.side_effect = [jobs0, jobs1, jobs2, jobs3]
        assert project._get_job_status_counts() == (0, 0)
        assert project._get_job_status_counts() == (0, 1)
        assert project._get_job_status_counts() == (1, 1)
        assert project._get_job_status_counts() == (1, 0)

    def test_wait_for_autopilot(self):
        def make_status(autopilot_done):
            return {'autopilot_done': autopilot_done}

        project = Project('p-id')
        with mock.patch.object(Project, '_autopilot_status_check') as mock_autopilot_check:
            mock_autopilot_check.side_effect = [make_status(False)] * 3 + \
                                               [make_status(True)] + \
                                               [make_status(False)]

            project.wait_for_autopilot(check_interval=.5, verbosity=0)
            assert mock_autopilot_check.call_count == 4

    def test_wait_for_autopilot_timeout(self):
        project = Project('p-id')
        with mock.patch.object(Project, '_autopilot_status_check') as mock_autopilot_check:
            mock_autopilot_check.return_value = {'autopilot_done': False}
            self.assertRaises(errors.AsyncTimeoutError,
                              project.wait_for_autopilot,
                              check_interval=10, verbosity=0, timeout=.2)

    def test_wait_for_autopilot_target_not_set_is_error(self):
        project = Project('p-id')
        with mock.patch.object(Project, 'get_status') as mock_get_status:
            mock_get_status.return_value = {'autopilot_done': False,
                                            'stage': PROJECT_STAGE.AIM}
            with pytest.raises(RuntimeError) as exc_info:
                project.wait_for_autopilot(check_interval=10, verbosity=0, timeout=.2)
            assert_raised_regex(exc_info, 'target has not been set')

    def test_wait_for_autopilot_mode_incorrect_is_error(self):
        project = Project('p-id')
        with mock.patch.multiple(
                Project,
                get_status=lambda _self: {'autopilot_done': False,
                                          'stage': PROJECT_STAGE.MODELING},
                _server_data=lambda _self, _: construct_dummy_aimed_project(autopilot_mode=2)):
            with pytest.raises(RuntimeError) as exc_info:
                project.wait_for_autopilot(check_interval=10, verbosity=0, timeout=.2)

            assert_raised_regex(exc_info, 'mode is not full auto')


class TestProjectList(SDKTestcase):

    def setUp(self):
        self.raw_return = """
        [
            {
            "project_name": "Api project",
            "_id": "54c627fa100d2b2c7002a489"
            },
            {
            "_id": "54c78125100d2b2fe3b296b6",
            "project_name": "Untitled project"
            }
        ]
        """

    @responses.activate
    def test_list_projects(self):
        """
        Test list projects
        """
        responses.add(responses.GET,
                      'https://host_name.com/projects/',
                      body=self.raw_return,
                      status=200,
                      content_type='application/json')
        project_lists = Project.list()
        assert isinstance(project_lists, list)
        assert project_lists[0].id == '54c627fa100d2b2c7002a489'
        assert project_lists[0].project_name == 'Api project'
        assert project_lists[1].id == '54c78125100d2b2fe3b296b6'
        assert project_lists[1].project_name == 'Untitled project'

    @responses.activate
    def test_with_manual_search_params(self):
        responses.add(responses.GET,
                      'https://host_name.com/projects/?projectName=x',
                      body=self.raw_return,
                      status=200,
                      content_type='application/json',
                      match_querystring=True)
        Project('p-id').list(search_params={'project_name': 'x'})
        self.assertEqual(
            responses.calls[0].request.url,
            'https://host_name.com/projects/?projectName=x')

    @responses.activate
    def test_with_bad_search_params(self):
        with self.assertRaises(TypeError):
            Project('p-id').list(search_params=12)


class TestGetModels(SDKTestcase, URLParamsTestCase):

    def setUp(self):
        super(TestGetModels, self).setUp()
        self.raw_data = """
        [
    {
    "featurelistId": "556cdfbd100d2b10048c7941",
    "processes": ["One", "Two", "Three"],
    "featurelistName": "Informative Features",
    "projectId": "p-id",
    "samplePct": 64,
    "modelType": "AVG Blender",
    "metrics": {
        "AUC": {
            "holdout": 0.76603,
            "validation": 0.64141,
            "crossValidation": 0.7625240000000001
        },
        "Rate@Top5%": {
            "holdout": 1,
            "validation": 0.5,
            "crossValidation": 0.9
        },
        "Rate@TopTenth%": {
            "holdout": 1,
            "validation": 1,
            "crossValidation": 1
        },
        "RMSE": {
            "holdout": 0.42054,
            "validation": 0.44396,
            "crossValidation": 0.40162000000000003
        },
        "LogLoss": {
            "holdout": 0.53707,
            "validation": 0.58051,
            "crossValidation": 0.5054160000000001
        },
        "FVE Binomial": {
            "holdout": 0.17154,
            "validation": 0.03641,
            "crossValidation": 0.17637399999999998
        },
        "Gini Norm": {
            "holdout": 0.53206,
            "validation": 0.28282,
            "crossValidation": 0.525048
        },
        "Rate@Top10%": {
            "holdout": 1,
            "validation": 0.25,
            "crossValidation": 0.7
        }
    },
    "blueprintId": "a4fd9d17a8ca62ee00590dd704dae6a8",
    "id": "556ce973100d2b6e51ca9657"
},
    {
    "featurelistId": "556cdfbd100d2b10048c7941",
    "processes": ["One", "Two", "Three"],
    "featurelistName": "Informative Features",
    "projectId": "p-id",
    "samplePct": 64,
    "modelType": "AVG Blender",
    "metrics": {
        "AUC": {
            "holdout": 0.76603,
            "validation": 0.64141,
            "crossValidation": 0.7625240000000001
        },
        "Rate@Top5%": {
            "holdout": 1,
            "validation": 0.5,
            "crossValidation": 0.9
        },
        "Rate@TopTenth%": {
            "holdout": 1,
            "validation": 1,
            "crossValidation": 1
        },
        "RMSE": {
            "holdout": 0.42054,
            "validation": 0.44396,
            "crossValidation": 0.40162000000000003
        },
        "LogLoss": {
            "holdout": 0.53707,
            "validation": 0.58051,
            "crossValidation": 0.5054160000000001
        },
        "FVE Binomial": {
            "holdout": 0.17154,
            "validation": 0.03641,
            "crossValidation": 0.17637399999999998
        },
        "Gini Norm": {
            "holdout": 0.53206,
            "validation": 0.28282,
            "crossValidation": 0.525048
        },
        "Rate@Top10%": {
            "holdout": 1,
            "validation": 0.25,
            "crossValidation": 0.7
        }
    },
    "blueprintId": "a4fd9d17a8ca62ee00590dd704dae6a8",
    "id": "556ce973100d2b6e51ca9658"
}
]
        """

    @responses.activate
    def test_get_models_ordered_by_metric_by_default(self):
        """
        Project('p-id').get_models()
        """
        responses.add(responses.GET,
                      'https://host_name.com/projects/p-id/models/?orderBy=-metric',
                      body=self.raw_data,
                      status=200,
                      content_type='application/json',
                      match_querystring=True)
        leaderboard = Project('p-id').get_models()
        self.assertNotEqual(0, len(leaderboard))
        for item in leaderboard:
            self.assertIsInstance(item, Model)
        self.assertEqual(leaderboard[0].id, '556ce973100d2b6e51ca9657')
        self.assertEqual(leaderboard[1].id, '556ce973100d2b6e51ca9658')
        self.assertEqual(leaderboard[0].project_id, 'p-id')
        self.assertEqual(leaderboard[1].project_id, 'p-id')

    @responses.activate
    def test_get_models_ordered_by_specific_field(self):
        # ordering
        responses.add(responses.GET,
                      'https://host_name.com/projects/p-id/models/?orderBy=samplePct',
                      body=self.raw_data,
                      status=200,
                      content_type='application/json',
                      match_querystring=True)
        Project('p-id').get_models(order_by='samplePct')
        self.assertEqual(
            responses.calls[0].request.url,
            'https://host_name.com/projects/p-id/models/?orderBy=samplePct')

    @responses.activate
    def test_get_models_orderd_by_two_fields(self):
        # ordering by two fields
        responses.add(
            responses.GET,
            'https://host_name.com/projects/p-id/models/?orderBy=samplePct%2C-metric',
            body=self.raw_data,
            status=200,
            content_type='application/json',
            match_querystring=True)
        Project('p-id').get_models(
            order_by=['sample_pct', '-metric'])
        self.assertEqual(
            responses.calls[0].request.url,
            'https://host_name.com/projects/p-id/models/?orderBy=samplePct%2C-metric')

    @responses.activate
    def test_get_models_two_order_fields_and_filtering(self):
        # ordering by two fields plus filtering
        responses.add(
            responses.GET,
            'https://host_name.com/projects/p-id/models/'
            '?withMetric=RMSE&orderBy=metric%2C-samplePct',
            body=self.raw_data,
            status=200,
            content_type='application/json',
            match_querystring=True)
        Project('p-id').get_models(
            order_by=['metric', '-sample_pct'], with_metric='RMSE')

    def test_order_by_with_unexpected_param_fails(self):
        with pytest.raises(ValueError) as exc_info:
            Project('p-id').get_models(order_by='someThing')
        assert_raised_regex(exc_info,  'Provided order_by attribute')

    def test_order_by_with_bad_param_fails(self):
        with pytest.raises(TypeError) as exc_info:
            Project('p-id').get_models(order_by=True)
        assert_raised_regex(exc_info, 'Provided order_by attribute')

    def test_with_bad_search_param_fails(self):
        with self.assertRaises(TypeError):
            Project('p-id').get_models(search_params=True)

    def _canonize_order_by_handles_none(self):
        proj = Project('p-id')
        self.assertIsNone(proj._canonize_order_by(None))


@responses.activate
@pytest.mark.usefixtures('client')
def retrieve_smart_sampled_project(project_url, project_id, smart_sampled_project_server_data):
    responses.add(responses.GET, project_url,
                  body=json.dumps(smart_sampled_project_server_data),
                  status=200, content_type='application/json')
    smart_sampled_project = Project.get(project_id)
    advanced = smart_sampled_project.advanced_options
    assert advanced['smart_downsampled'] is True
    rate_key = 'majority_downsampling_rate'
    assert advanced[rate_key] == smart_sampled_project_server_data[rate_key]
