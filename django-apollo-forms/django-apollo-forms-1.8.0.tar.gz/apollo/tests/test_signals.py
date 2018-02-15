from django.test import TestCase
from apollo.factories import FormFieldFactory, FormFactory, FormSubmissionFactory, ExternalWebhookFactory
from apollo import signals, models, settings
import requests
import responses
import mock


class SignalTestCase(TestCase):
    pass


class TestFireExternalWebhooksSignal(SignalTestCase):
    def setUp(self):
        super(TestFireExternalWebhooksSignal, self).setUp()

        self.form = FormFactory(allow_webhooks=True)
        self.hook = ExternalWebhookFactory(form=self.form, url='https://test.com', for_event=models.ExternalWebhook.EVENT_SUBMISSION_CREATED)
        self.submission = FormSubmissionFactory(
            form=self.form,
            raw_data={},
            cleaned_data={'first_name': 'Bobby', 'last_name': 'S', 'email': 'test@test.com'},
            is_valid=True
        )

    @mock.patch('apollo.models.ExternalWebhook.send_data')
    def test_calls_webhook_send_data_with_submission_data(self, mock_send_data):
        mock_send_data.return_value = responses.Response(status=200, method='POST', url=self.hook.url)

        signals.fire_form_submission_webhooks(None, self.submission.cleaned_data, self.form.id, self.submission.id)

        self.assertIsNone(
            # we could use FormSubmissionSerializer(instance=submission).data here, but I think this is clearer
            mock_send_data.assert_called_once_with({
                'id': self.submission.id,
                'cleaned_data': self.submission.cleaned_data,
                'raw_data': self.submission.raw_data,
                'created_time': self.submission.created_time.strftime('%Y-%m-%dT%H:%M:%S.%fZ'),
                'form': self.form.id,
                'is_valid': True,
                'label': self.submission.label
            })
        )

