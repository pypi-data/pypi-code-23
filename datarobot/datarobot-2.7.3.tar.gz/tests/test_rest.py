import json

import pytest
import responses

from datarobot import Project, AppPlatformError
from datarobot import errors
from .utils import SDKTestcase, assert_raised_regex


class Test400LevelErrors(SDKTestcase):

    @responses.activate
    def test_401_error_message(self):
        """For whatever reason, the `requests` library completely ignores the
        body in a 401 error, so, here is our own message
        """
        responses.add(
            responses.GET,
            'https://host_name.com/projects/',
            status=401,
        )

        with pytest.raises(AppPlatformError) as exc_info:
            Project.list()
        assert_raised_regex(exc_info, 'not properly authenticated')

    @responses.activate
    def test_403_error_message(self):
        """ Check that we output same error message that server returns on 403
        """
        error_text = 'Some permission error'
        error_response = {'message': error_text}

        responses.add(
            responses.GET,
            'https://host_name.com/projects/',
            status=403,
            body=json.dumps(error_response)
        )

        with pytest.raises(AppPlatformError) as exc_info:
            Project.list()
        expected_error = '{} client error: {}'.format(403, json.dumps(error_response))
        assert str(exc_info.value) == expected_error

    @responses.activate
    def test_model_already_added_exception(self):
        responses.add(
            responses.POST,
            'https://host_name.com/projects/p-id/models/',
            status=422,
            body=json.dumps({'message': u'Model already added', 'errorName': u'JobAlreadyAdded'})
        )

        with pytest.raises(errors.JobAlreadyRequested):
            Project('p-id').train('some-blueprint-id')

    @responses.activate
    def test_extracts_error_message(self):
        data = {'message': 'project p-id has been deleted'}
        responses.add(responses.GET, 'https://host_name.com/projects/p-id/models/',
                      status=422,
                      body=json.dumps(data),
                      content_type='application/json')

        with pytest.raises(AppPlatformError) as exc_info:
            Project('p-id').get_models()
        assert_raised_regex(exc_info, 'project p-id has been deleted')
