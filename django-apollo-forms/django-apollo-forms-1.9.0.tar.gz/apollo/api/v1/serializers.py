from django.core.exceptions import ObjectDoesNotExist, ValidationError
from rest_framework import serializers
from apollo.models import Layout, LayoutField, FormField, FormFieldTemplate, Form, FormSubmission, ExternalWebhook
from apollo import signals
from apollo.settings import apollo_settings
from apollo.lib import emails
import logging
import pdb

logger = logging.getLogger(__name__)


class LayoutBlockSerializer(serializers.ModelSerializer):
    def create(self, validated_data):
        return LayoutField.objects.create(**validated_data)

    class Meta:
        model = LayoutField
        fields = ['id', 'desktop_width', 'desktop_height', 'desktop_top_left', 'mobile_width', 'mobile_height',
                  'mobile_top_left']


class LayoutSerializer(serializers.ModelSerializer):
    blocks = LayoutBlockSerializer(many=True)

    class Meta:
        model = Layout
        fields = ['id', 'name', 'max_width', 'blocks']


class FormFieldTemplateSerializer(serializers.ModelSerializer):
    class Meta:
        model = FormFieldTemplate
        fields = ['id', 'name', 'input_type', 'is_visible', 'label', 'label_position', 'placeholder', 'default_value',
                  'value_choices', 'validation_rule', 'is_submission_label']


class FieldOptionsSerializer(serializers.Serializer):
    widget_types = serializers.ListField(child=serializers.CharField())
    validation_rules = serializers.ListField(child=serializers.CharField())
    label_positions = serializers.ListField(child=serializers.CharField())


class FormFieldSerializer(serializers.ModelSerializer):
    name = serializers.CharField()
    input_type = serializers.CharField()
    is_visible = serializers.BooleanField(default=True)
    is_submission_label = serializers.BooleanField(default=False)

    def create(self, validated_data):
        field_name = validated_data.pop('name')

        template = FormFieldTemplate.objects.get(name=field_name)

        # clear out the template fields from the data, they will break things
        template_fields = ('input_type', 'is_visible', 'is_submission_label')
        [validated_data.pop(f) for f in template_fields]

        return FormField.objects.create(template=template, **validated_data)

    def update(self, instance, validated_data):
        # clear out the template fields from the data, they will break things
        template_fields = ('name', 'input_type', 'is_visible', 'is_submission_label')
        [validated_data.pop(f) for f in template_fields]

        return super(FormFieldSerializer, self).update(instance, validated_data)

    class Meta:
        model = FormField
        fields = ['id', 'name', 'input_type', 'is_visible', 'label', 'label_position', 'placeholder', 'default_value',
                  'value_choices', 'validation_rule', 'is_submission_label', 'index']


class FormSerializer(serializers.ModelSerializer):
    fields = FormFieldSerializer(many=True)

    def create(self, validated_data):
        fields = validated_data.pop('fields')

        form = Form.objects.create(**validated_data)

        self._handle_raw_fields(form, fields)

        form.save()

        return form

    def update(self, instance, validated_data):
        fields = validated_data.pop('fields')

        # check if any fields were removed from the form and delete them if so
        old_field_names = set(instance.fields.values_list('template__name', flat=True))
        new_field_names = {f['name'] for f in fields}

        to_delete = instance.fields.filter(template__name__in=old_field_names.difference(new_field_names))

        logger.debug('about to delete %s form fields' % to_delete.count())

        to_delete.delete()

        self._handle_raw_fields(instance, fields)

        return super(FormSerializer, self).update(instance, validated_data)

    def _handle_raw_fields(self, form, raw_fields):
        for field_dat in raw_fields:
            try:
                field = form.fields.get(template__name=field_dat['name'])
            except ObjectDoesNotExist:
                field = None

            field_serializer = FormFieldSerializer(field, data=field_dat)

            if field_serializer.is_valid(raise_exception=True):
                field_serializer.save(form=form)

    class Meta:
        model = Form
        fields = ['id', 'name', 'redirect_url', 'success_message', 'submit_button_text', 'submission_url',
                  'submission_contacts', 'allow_webhooks', 'fields']


class FormSubmissionSerializer(serializers.ModelSerializer):
    cleaned_data = serializers.DictField(read_only=True)
    is_valid = serializers.BooleanField(read_only=True)

    def create(self, validated_data):
        form = validated_data.get('form')

        signals.form_submitted.send(
            sender=FormSubmissionSerializer,
            form_id=form.id,
            raw_data=validated_data
        )

        submission = FormSubmission(raw_data=validated_data['raw_data'], form=form)
        error_msg = False

        try:
            submission.clean_data()
        except ValueError as exc:
            error_msg = 'got error cleaning submission data'
        except ValidationError as exc:
            error_msg = 'got error validating submission data'
        finally:
            submission.save()

        if error_msg:
            signals.form_submission_error.send(
                sender=FormSubmissionSerializer,
                form_id=submission.form_id,
                raw_data=submission.raw_data,
                error=error_msg
            )

            raise ValidationError(error_msg)

        if form.submission_contacts and apollo_settings.SUBMISSION_EMAIL_FROM:
            emails.send(
                from_email=apollo_settings.SUBMISSION_EMAIL_FROM,
                to_emails=form.submission_contacts,
                subject='Apollo: New Form Submission',
                content='new form submission, data = %s' % str(submission.cleaned_data)
            )

        signals.form_submission_cleaned.send(
            sender=FormSubmissionSerializer,
            form_id=submission.form_id,
            submission_id=submission.id,
            cleaned_data=submission.cleaned_data
        )

        return submission

    class Meta:
        model = FormSubmission
        fields = ['id', 'cleaned_data', 'raw_data', 'is_valid', 'created_time', 'form', 'label']


class ExternalWebhookSerializer(serializers.ModelSerializer):
    def validate_form(self, value):
        # if the form doesn't allow webhooks, thats an error
        if not value.allow_webhooks:
            raise ValidationError('form %s doesnt allow external webhooks. Set allow_webhooks = True and try again.' % value)

        return value

    class Meta:
        model = ExternalWebhook
        fields = ['id', 'form', 'url', 'for_event', 'service']