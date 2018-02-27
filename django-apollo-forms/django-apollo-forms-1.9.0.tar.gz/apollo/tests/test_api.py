from django.test import TestCase, Client, RequestFactory
from contextlib import contextmanager
from rest_framework.test import APIClient
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError, ObjectDoesNotExist
from django.contrib.auth.models import Permission
from rest_framework.authtoken.models import Token
from apollo.factories import FormFactory, FormFieldFactory, FormFieldTemplateFactory, FormSubmissionFactory, APIUserFactory
from apollo.models import Form, FormFieldTemplate, ExternalWebhook
from apollo.settings import apollo_settings
from apollo.api.v1.serializers import FormSerializer, FormFieldSerializer
from apollo import signals
import os
import factory
import mock
import json
import pdb
import logging
import re
import copy

logger = logging.getLogger(__name__)


class APITestCase(TestCase):
    base_path = '/api'
    version = 'v1'
    should_login = True
    user_username = 'tester'
    user_password = 'mytestapi'

    def setUp(self):
        self.client = APIClient()

        self.user = User.objects.create_user(username=self.user_username, email='test@test.com', password=self.user_password)

        if self.should_login:
            self.login_client()

        patch_send_email = mock.patch('apollo.lib.emails.send', return_value=True)
        self.mock_send_email = patch_send_email.start()

        self.addCleanup(patch_send_email.stop)

    def add_permission(self, codename):
        perm = Permission.objects.get(codename=codename)
        self.user.user_permissions.add(perm)

    def remove_permission(self, codename):
        perm = Permission.objects.get(codename=codename)
        self.user.user_permissions.remove(perm)

    def abs_path(self, path):
        return '%s/%s%s' % (self.base_path, self.version, path)

    def login_client(self, auth_params=None):
        auth_params = auth_params or {'username': 'tester', 'password': 'mytestapi'}

        self.client.login(**auth_params)

    def post(self, path, params=None):
        params = params or {}

        return self.client.post(self.abs_path(path), params, format='json')

    def put(self, path, params=None):
        params = params or {}
        return self.client.put(self.abs_path(path), data=params, format='json')

    def delete(self, path, params=None):
        params = params or {}
        return self.client.delete(self.abs_path(path), data=params, format='json')

    def get(self, path, params=None):
        return self.client.get(self.abs_path(path), data=params, format='json')


#####-----< Forms API >----#####
#####-----< Forms API >----#####
class FormsAPITestCase(APITestCase):
    def setUp(self):
        super(FormsAPITestCase, self).setUp()

        self._first_name_template = FormFieldTemplateFactory(name='first_name', input_type='TEXT', is_visible=True)
        self._last_name_template = FormFieldTemplateFactory(name='last_name', input_type='TEXT', is_visible=True)


class TestCreateForm(FormsAPITestCase):
    def setUp(self):
        super(TestCreateForm, self).setUp()

        self.form_data = {
            'name': 'Test Form',
            'redirect_url': 'http://test.com',
            'submit_button_text': 'Submit',
            'submission_url': '/submissions',
            'fields': [
                {
                    'name': 'first_name',
                    'input_type': 'TEXT',
                    'is_visible': True,
                    'placeholder': 'First Name'
                },
                {
                    'name': 'last_name',
                    'input_type': 'TEXT',
                    'is_visible': True,
                    'placeholder': 'Last Name'
                }
            ]
        }

        self.add_permission('add_form')

    def test_create_form_with_basic_data(self):
        resp = self.post('/forms', self.form_data)

        self.assertEqual(resp.status_code, 201)

        form = Form.objects.get(id=resp.json()['id'])

        self.assertEqual(form.name, self.form_data['name'])
        self.assertEqual(form.redirect_url, self.form_data['redirect_url'])
        self.assertEqual(form.submit_button_text, self.form_data['submit_button_text'])
        self.assertEqual(form.submission_url, self.form_data['submission_url'])

        for field in self.form_data['fields']:
            try:
                ff = form.fields.get(template__name=field['name'])
            except ObjectDoesNotExist:
                self.fail('%s was never created for form %s' % (field['name'], form))

            for attr, val in field.items():
                self.assertEqual(getattr(ff, attr), val)

    def test_create_form_perms_required_to_create_form(self):
        self.remove_permission('add_form')

        resp = self.post('/forms', self.form_data)

        self.assertEqual(resp.status_code, 403)


class TestUpdateForm(FormsAPITestCase):
    def setUp(self):
        super(TestUpdateForm, self).setUp()

        self.form = FormFactory(name='Test Form', redirect_url='http://test.com', submit_button_text='Submit')
        self.first_name_field = FormFieldFactory(template=self._first_name_template, placeholder='First Name', form=self.form)
        self.last_name_field = FormFieldFactory(template=self._last_name_template, placeholder='Last Name', form=self.form)

        self.form_data_template = {
            'name': self.form.name,
            'redirect_url': self.form.redirect_url,
            'submit_button_text': self.form.submit_button_text,
            'submission_url': self.form.submission_url,
            'fields': [
                {
                    'name': f.name,
                    'input_type': f.input_type,
                    'is_visible': f.is_visible,
                    'placeholder': f.placeholder
                } for f in (self.first_name_field, self.last_name_field)
            ]
        }

        self.add_permission('change_form')

    def test_update_form_meta(self):
        update_data = copy.deepcopy(self.form_data_template)

        update_data.update({
            'name': 'Test Form 2',
            'redirect_url': 'https://test.com'
        })

        resp = self.put('/forms/%s' % self.form.id, update_data)

        self.assertEqual(resp.status_code, 200)

        self.form.refresh_from_db()

        self.assertEqual(self.form.name, update_data['name'])
        self.assertEqual(self.form.redirect_url, update_data['redirect_url'])
        self.assertEqual(self.form.submit_button_text, self.form_data_template['submit_button_text'])
        self.assertEqual(self.form.submission_url, self.form_data_template['submission_url'])

    def test_update_form_fields(self):
        update_data = copy.deepcopy(self.form_data_template)

        update_data.update({
            'fields': [
                {
                    'name': 'first_name',
                    'input_type': 'TEXT',
                    'is_visible': True,
                    'placeholder': 'Nickname'
                },
                {
                    'name': 'last_name',
                    'input_type': 'TEXT',
                    'is_visible': True,
                    'placeholder': 'Last'
                }
            ]
        })

        self.put('/forms/%s' % self.form.id, update_data)

        self.first_name_field.refresh_from_db()
        self.last_name_field.refresh_from_db()

        self.assertEqual(self.first_name_field.placeholder, 'Nickname')
        self.assertEqual(self.last_name_field.placeholder, 'Last')

    def test_remove_form_field(self):
        update_data = copy.deepcopy(self.form_data_template)

        update_data.update({
            'fields': [
                {
                    'name': 'first_name',
                    'input_type': 'TEXT',
                    'is_visible': True,
                    'placeholder': 'First Name'
                }
            ]
        })

        self.put('/forms/%s' % self.form.id, update_data)

        self.form.refresh_from_db()

        self.assertEqual(self.form.fields.count(), 1)
        self.assertRaises(ObjectDoesNotExist, self.last_name_field.refresh_from_db)

    def test_add_form_field(self):
        FormFieldTemplateFactory(name='email', input_type='EMAIL', is_visible=True)

        update_data = copy.deepcopy(self.form_data_template)

        update_data.update({
            'fields': [
                {
                    'name': 'first_name',
                    'input_type': 'TEXT',
                    'is_visible': True,
                    'placeholder': 'First Name'
                },
                {
                    'name': 'last_name',
                    'input_type': 'TEXT',
                    'is_visible': True,
                    'placeholder': 'Last Name'
                },
                {
                    'name': 'email',
                    'input_type': 'EMAIL',
                    'is_visible': True,
                    'placeholder': 'Email'
                },
            ]
        })

        self.put('/forms/%s' % self.form.id, update_data)

        self.form.refresh_from_db()

        self.assertEqual(self.form.fields.count(), 3)
        self.assertListEqual(
            list(self.form.fields.values_list('template__name', flat=True).order_by('template__name')),
            sorted(['first_name', 'last_name', 'email'])
        )

    def test_change_permissions_required_to_change_form(self):
        self.remove_permission('change_form')

        update_data = copy.deepcopy(self.form_data_template)

        update_data.update({
            'name': 'Test Form 2',
            'redirect_url': 'https://test.com'
        })

        resp = self.put('/forms/%s' % self.form.id, update_data)

        self.assertEqual(resp.status_code, 403)


class TestRetrieveForm(FormsAPITestCase):
    def setUp(self):
        super(TestRetrieveForm, self).setUp()

        self.form = FormFactory()
        self.first_name_field = FormFieldFactory(validation_rule='REQUIRED', template=self._first_name_template, form=self.form)
        self.last_name_field = FormFieldFactory(validation_rule='REQUIRED', template=self._last_name_template, form=self.form)

    def test_retrieve_basic_form_data(self):
        resp = self.get('/forms/%s' % self.form.id)

        form_data = resp.json()

        self.assertEqual(form_data['name'], self.form.name)
        self.assertEqual(form_data['submission_url'], self.form.submission_url)
        self.assertEqual(form_data['redirect_url'], self.form.redirect_url)

        for field in self.form.fields.all():
            dat_field = [f for f in form_data['fields'] if f['name'] == field.name][0]

            self.assertEqual(dat_field['name'], field.name)
            self.assertEqual(dat_field['input_type'], field.input_type)
            self.assertEqual(dat_field['validation_rule'], field.validation_rule)

    def test_no_perms_required_to_retrieve_form_data(self):
        self.client.logout()

        resp = self.get('/forms/%s' % self.form.id)

        self.assertEqual(resp.status_code, 200)


class TestCloneForm(FormsAPITestCase):
    def setUp(self):
        super(TestCloneForm, self).setUp()

        self.form = FormFactory()

        self.add_permission('add_form')

    @mock.patch('apollo.models.Form.clone')
    def test_clone_form_calls_clone_method(self, mock_clone):
        resp = self.post('/forms/%s/clone' % self.form.id)

        self.assertEqual(mock_clone.call_count, 1)

    def test_clone_form_returns_clone(self):
        resp = self.post('/forms/%s/clone' % self.form.id)

        self.assertEqual(resp.status_code, 201)

        self.assertGreater(resp.json()['id'], self.form.id)

    def test_clone_form_requires_add_form_permission(self):
        self.remove_permission('add_form')

        resp = self.post('/forms/%s/clone' % self.form.id)

        self.assertEqual(resp.status_code, 403)


#####-----< FormFieldTemplate API >----#####
#####-----< FormFieldTemplate API >----#####
class TestCreateFormFieldTemplate(APITestCase):
    def setUp(self):
        super(TestCreateFormFieldTemplate, self).setUp()

        self.field_template_data = {
            'name': 'first_name',
            'input_type': 'TEXT',
            'is_visible': True,
            'label': 'First Name',
            'placeholder': 'First Name',
            'validation_rule': 'REQUIRED'
        }

        self.add_permission('add_formfieldtemplate')

    def test_create_basic_form_field_template(self):
        resp = self.post('/field-templates', self.field_template_data)

        self.assertEqual(resp.status_code, 201)

        resp_data = resp.json()

        created_template = FormFieldTemplate.objects.get(id=resp_data['id'])

        for k, v in self.field_template_data.items():
            self.assertEqual(getattr(created_template, k), v)

    def test_creating_form_field_template_requires_create_form_field_template_permission(self):
        self.remove_permission('add_formfieldtemplate')

        resp = self.post('/field-templates', self.field_template_data)

        self.assertEqual(resp.status_code, 403)


class TestUpdateFormFieldTemplate(APITestCase):
    def setUp(self):
        super(TestUpdateFormFieldTemplate, self).setUp()

        self.field_template = FormFieldTemplateFactory(name='email', input_type='EMAIL', placeholder='Email', label='Email')

        self.field_template_data = {
            'name': self.field_template.name,
            'input_type': self.field_template.input_type,
            'is_visible': self.field_template.is_visible,
            'label': self.field_template.label,
            'placeholder': self.field_template.placeholder,
            'validation_rule': self.field_template.validation_rule
        }

        self.add_permission('change_formfieldtemplate')

    def test_changing_field_value(self):
        update_data = copy.deepcopy(self.field_template_data)

        update_data.update({
            'input_type': 'TEXT',
            'label': None,
        })

        resp = self.put('/field-templates/%s' % self.field_template.id, update_data)

        self.assertEqual(resp.status_code, 200)

        self.field_template.refresh_from_db()

        self.assertEqual(self.field_template.input_type, update_data['input_type'])
        self.assertEqual(self.field_template.label, update_data['label'])
        self.assertEqual(self.field_template.name, self.field_template_data['name'], 'the field name should not have changed')

    def test_change_form_field_template_requires_change_form_field_template_permission(self):
        self.remove_permission('change_formfieldtemplate')

        resp = self.post('/field-templates', self.field_template_data)

        self.assertEqual(resp.status_code, 403)


#####-----< FormField API >----#####
#####-----< FormField API >----#####
## TODO: FILL ME IN ##


#####-----< Submissions API >----#####
#####-----< Submissions API >----#####
class TestCreateFormSubmission(APITestCase):
    def setUp(self):
        super(TestCreateFormSubmission, self).setUp()

        # set up DB constructs
        self.form = FormFactory(id=1, name='Test Form')
        FormFieldFactory(form=self.form, template=FormFieldTemplateFactory(name='test'))

        self.submission_data = {
            'form': 1,
            'raw_data': [
                {
                    'id': 1,
                    'name': 'test',
                    'input_type': 'TEXT',
                    'is_visible': True,
                    'label': 'Test',
                    'validation_rule': 'OPTIONAL',
                    'value': 'Testy',
                }
            ]
        }

    @factory.django.mute_signals(signals.form_submission_cleaned)
    def test_returns_status_of_success_on_success(self):
        with mock.patch('apollo.models.FormSubmission.clean_data', return_value={}) as mock_clean_data:
            resp = self.post('/submissions', self.submission_data)

            self.assertEqual(mock_clean_data.call_count, 1)
            self.assertEqual(resp.status_code, 201)
            self.assertGreater(resp.json()['id'], 0)

    @factory.django.mute_signals(signals.form_submission_cleaned)
    def test_returns_status_of_error_on_value_error(self):
        with mock.patch('apollo.models.FormSubmission.clean_data', side_effect=ValueError) as mock_clean_data:
            resp = self.post('/submissions', self.submission_data)

            self.assertEqual(resp.status_code, 400)
            self.assertEqual(mock_clean_data.call_count, 1)
            self.assertEqual(resp.json()['error'], 'got error cleaning submission data')

    def test_returns_status_of_error_on_validation_error(self):
        with mock.patch('apollo.models.FormSubmission.clean_data', side_effect=ValidationError('error validating')) as mock_clean_data:
            resp = self.post('/submissions', self.submission_data)

            self.assertEqual(resp.status_code, 400)
            self.assertEqual(mock_clean_data.call_count, 1)
            self.assertEqual(resp.json()['error'], 'got error validating submission data')

    @factory.django.mute_signals(signals.form_submission_cleaned)
    def test_creates_new_submission_instance_when_clean_succeeds(self):
        resp = self.post('/submissions', self.submission_data)

        created_submission = self.form.submissions.first()

        self.assertDictEqual(
            created_submission.raw_data[0],
            self.submission_data['raw_data'][0]
        )
        self.assertDictEqual(created_submission.cleaned_data, {'test': 'Testy'})

    def test_still_creates_submission_when_clean_fails(self):
        with mock.patch('apollo.models.FormSubmission.clean_data', side_effect=ValidationError('error validating')) as mock_clean_data:
            resp = self.post('/submissions', self.submission_data)

            self.assertEqual(resp.status_code, 400)
            self.assertEqual(self.form.submissions.count(), 1)
            self.assertIsNone(self.form.submissions.first().cleaned_data)

    @factory.django.mute_signals(signals.form_submission_cleaned)
    def test_sends_email_to_submission_contacts_when_set(self):
        resp = self.post('/submissions', self.submission_data)

        self.assertEqual(self.mock_send_email.call_count, 0, "shouldnt send email when form has no submission contacts")

        # now try with submission contacts
        self.form.submission_contacts = ['bobby@classaction.com']
        self.form.save()

        self.post('/submissions', self.submission_data)

        self.assertEqual(self.mock_send_email.call_count, 1)
        self.assertIsNone(
            self.mock_send_email.assert_called_with(
                from_email=apollo_settings.SUBMISSION_EMAIL_FROM,
                to_emails=[u'bobby@classaction.com'],
                subject='Apollo: New Form Submission',
                content='new form submission, data = %s' % {u'test': u'Testy'}
            )
        )

    @factory.django.mute_signals(signals.form_submission_cleaned)
    def test_no_perms_required_to_create_submission(self):
        self.client.logout()

        resp = self.post('/submissions', self.submission_data)

        self.assertEqual(resp.status_code, 201)


class TestListFormSubmissions(FormsAPITestCase):
    def setUp(self):
        super(TestListFormSubmissions, self).setUp()

        self.add_permission('can_view_submissions')
        self.add_permission('change_formsubmission')
        self.add_permission('delete_formsubmission')

        self.form = FormFactory(name='Test Form')
        self.first_name_field = FormFieldFactory(template=self._first_name_template, form=self.form, placeholder='First Name')
        self.last_name_field = FormFieldFactory(template=self._last_name_template, form=self.form, placeholder='Last Name')

    def test_basic_list_submissions(self):
        submissions = []
        for field in (self.first_name_field, self.last_name_field):
            submissions.append(FormSubmissionFactory(form=self.form, raw_data={
                'id': field.id,
                'name': field.name,
                'input_type': field.input_type,
                'is_visible': field.is_visible,
                'value': factory.Faker(field.name).generate({})
            }))

        resp = self.get('/submissions')

        self.assertEqual(resp.status_code, 200)

        self.assertListEqual(sorted([s['id'] for s in resp.json()]), sorted([s.id for s in submissions]))

    def test_filtering_submissions_by_form(self):
        other_form = FormFactory(name='Some Form')
        other_submissions = FormSubmissionFactory(form=other_form, raw_data={})

        submissions = []
        for field in (self.first_name_field, self.last_name_field):
            submissions.append(FormSubmissionFactory(form=self.form, raw_data={
                'id': field.id,
                'name': field.name,
                'input_type': field.input_type,
                'is_visible': field.is_visible,
                'value': factory.Faker(field.name).generate({})
            }))

        resp = self.get('/submissions', params={'form_id': self.form.id})

        self.assertListEqual(sorted([s['id'] for s in resp.json()]), sorted([s.id for s in self.form.submissions.all()]))

    def test_can_view_submissions_permission_required_to_view_submissions(self):
        self.remove_permission('can_view_submissions')

        resp = self.get('/submissions')

        self.assertEqual(resp.status_code, 403)

    def test_can_change_submission_permissions_required_to_update_submission(self):
        submission = FormSubmissionFactory(
            form=self.form,
            raw_data={'fields': [{'name': 'first_name', 'value': 'bobby'}, {'name': 'last_name', 'value': 'stein'}]}
        )

        self.remove_permission('change_formsubmission')

        resp = self.put('/submissions/%s' % submission.id, params={'raw_data': { 'is_valid': False }, 'form': self.form.id})

        self.assertEqual(resp.status_code, 403)

    def test_can_delete_form_submission_permissions_required_to_delete_submission(self):
        submission = FormSubmissionFactory(
            form=self.form,
            raw_data={'fields': [{'name': 'first_name', 'value': 'bobby'}, {'name': 'last_name', 'value': 'stein'}]}
        )

        self.remove_permission('delete_formsubmission')

        resp = self.delete('/submissions/%s' % submission.id)

        self.assertEqual(resp.status_code, 403)


class TestTokenAuthentication(FormsAPITestCase):
    should_login = False

    def setUp(self):
        super(TestTokenAuthentication, self).setUp()

        self.api_user = APIUserFactory(auth_user=self.user)

        self.add_permission('can_view_submissions')

        self.form = FormFactory(name='Test Form')
        self.first_name_field = FormFieldFactory(template=self._first_name_template, form=self.form, placeholder='First Name')
        self.last_name_field = FormFieldFactory(template=self._last_name_template, form=self.form, placeholder='Last Name')

    def test_api_user_with_auth_token_can_read_form_submissions(self):
        submissions = []

        for field in (self.first_name_field, self.last_name_field):
            submissions.append(FormSubmissionFactory(form=self.form, raw_data={
                'id': field.id,
                'name': field.name,
                'input_type': field.input_type,
                'is_visible': field.is_visible,
                'value': factory.Faker(field.name).generate({})
            }))

        self.client.credentials(HTTP_AUTHORIZATION='Token ' + Token.objects.get(user=self.user).key)
        resp = self.get('/submissions')

        self.assertEqual(resp.status_code, 200)

        self.assertListEqual(sorted([s['id'] for s in resp.json()]), sorted([s.id for s in submissions]))


class TestRetrieveAuthToken(FormsAPITestCase):
    should_login = False

    def setUp(self):
        super(TestRetrieveAuthToken, self).setUp()

        self.api_user = APIUserFactory(auth_user=self.user)

    def test_passing_incorrect_creds_returns_400(self):
        resp = self.post('/auth-token', {'username': 'badusername', 'password': 'badpass'})

        self.assertEqual(resp.status_code, 400)

    def test_passing_correct_creds_returns_200_and_token(self):
        resp = self.post('/auth-token', {'username': self.user_username, 'password': self.user_password})

        self.assertEqual(resp.status_code, 200)
        self.assertDictEqual(resp.json(), {'token': Token.objects.get(user=self.user).key})


class TestExternalWebhookRegistration(FormsAPITestCase):
    def setUp(self):
        super(TestExternalWebhookRegistration, self).setUp()

        self.add_permission('add_externalwebhook')
        self.add_permission('delete_externalwebhook')

    def test_allows_registration_to_form_with_allow_webhooks(self):
        form = FormFactory(allow_webhooks=True)

        data = {'service': 'zapier', 'for_event': ExternalWebhook.EVENT_SUBMISSION_CREATED, 'url': 'https://test.com', 'form': form.id}

        resp = self.post('/hooks', data)

        self.assertEqual(resp.status_code, 201)

        hook = ExternalWebhook.objects.get(id=resp.json()['id'])

        self.assertEqual(hook.service, data['service'])
        self.assertEqual(hook.for_event, data['for_event'])
        self.assertEqual(hook.url, data['url'])

    def test_doesnt_allow_registration_to_form_without_allow_webhooks(self):
        form = FormFactory(allow_webhooks=False)

        data = {'service': 'zapier', 'for_event': ExternalWebhook.EVENT_SUBMISSION_CREATED, 'url': 'https://test.com', 'form': form.id}

        resp = self.post('/hooks', data)

        self.assertEqual(resp.status_code, 400)
        print(resp.content)

    def test_only_allows_webhook_creation_and_deletion(self):
        pass