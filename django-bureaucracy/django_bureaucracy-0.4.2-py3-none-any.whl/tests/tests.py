import os

import django
from bureaucracy.tests.factories import StaffFactory, SuperUserFactory
from django.core.exceptions import ValidationError
from django.core.files import File
from django.core.urlresolvers import reverse
from django.test import override_settings
from django_bureaucracy.models import Document
from django_bureaucracy.shortcuts import (render_to_docx_response,
                                          render_to_pdf_response)

resources_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'resources')


class DocumentModelTests(django.test.TestCase):
    def setUp(self):
        self.user = StaffFactory.create()

    @override_settings(DOCX_TEMPLATE_VARS={'doctype': ('foo', 'bar', 'baz')})
    def test_template_clean(self):
        doc = Document(uploader=self.user, validate_fields=True, type='doctype')
        doc.template_file = File(open(os.path.join(resources_dir, 'simple_fields.docx'), 'rb'))
        doc.clean()

    @override_settings(DOCX_TEMPLATE_VARS={'doctype': ('foo', 'bar', 'baz', 'missing_from_tpl')})
    def test_template_clean_fails_missing_fields(self):
        doc = Document(uploader=self.user, validate_fields=True, type='doctype')
        doc.template_file = File(open(os.path.join(resources_dir, 'simple_fields.docx'), 'rb'))

        with self.assertRaises(ValidationError) as e:
            doc.clean()

        self.assertEqual(len(e.exception.error_dict), 1)
        self.assertEqual(len(e.exception.error_dict['template_file']), 1)

        self.assertEqual(e.exception.error_dict['template_file'][0].message,
                         "Mailmerge fields in template did not match the ones configured for this type."
                         "missing: {missing}, superfluous: {superfluous}".format(missing={'missing_from_tpl'},
                                                                                 superfluous=set()))

    @override_settings(DOCX_TEMPLATE_VARS={'doctype': ('foo', 'bar')})
    def test_template_clean_fails_superfluous_fields(self):
        doc = Document(uploader=self.user, validate_fields=True, type='doctype')
        doc.template_file = File(open(os.path.join(resources_dir, 'simple_fields.docx'), 'rb'))

        with self.assertRaises(ValidationError) as e:
            doc.clean()

        self.assertEqual(len(e.exception.error_dict), 1)
        self.assertEqual(len(e.exception.error_dict['template_file']), 1)

        self.assertEqual(e.exception.error_dict['template_file'][0].message,
                         "Mailmerge fields in template did not match the ones configured for this type."
                         "missing: {missing}, superfluous: {superfluous}".format(missing=set(),
                                                                                 superfluous={'baz'}))

    @override_settings(DOCX_TEMPLATE_VARS={'doctype': ('foo', 'lolwat')})
    def test_no_validation(self):
        doc = Document(uploader=self.user, validate_fields=False, type='doctype')
        doc.template_file = File(open(os.path.join(resources_dir, 'simple_fields.docx'), 'rb'))

        # clean should not raise a ValidationError because validate_fields is False
        doc.clean()


class DjangoResponseTests(django.test.TestCase):
    def test_docx_response(self):
        resp = render_to_docx_response(os.path.join(resources_dir, 'simple_fields.docx'),
                                       {'foo': 'frobnicate',
                                        'bar': 'determiorate',
                                        'baz': 'some kind of string'})
        self.assertEqual(resp['Content-Type'],
                         'application/vnd.openxmlformats-officedocument.wordprocessingml.document')

    def test_pdf_response(self):
        resp = render_to_pdf_response(os.path.join(resources_dir, 'simple_fields.docx'),
                                      {'foo': 'frobnicate',
                                       'bar': 'determiorate',
                                       'baz': 'some kind of string'})
        self.assertEqual(resp['Content-Type'], 'application/pdf')


class DjangoAdminTest(django.test.TestCase):
    def setUp(self):
        self.user = SuperUserFactory()

    def test_admin(self):

        self.client.login(username=self.user.username, password='hunter2')

        with open(os.path.join(resources_dir, 'simple_fields.docx'), 'rb') as f:
            resp = self.client.post(reverse('admin:django_bureaucracy_document_add'),
                                    data={'template_file': f, 'type': 'doctype', 'validate_fields': False})

        self.assertEqual(resp.status_code, 302)

        self.assertEqual(Document.objects.get().uploader, self.user)
