import factory
from apollo import models


class FormFactory(factory.django.DjangoModelFactory):
    name = factory.Faker('name')
    redirect_url = factory.Faker('url')
    submission_url = factory.Faker('uri_page')

    class Meta:
        model = models.Form


class FormFieldTemplateFactory(factory.django.DjangoModelFactory):
    name = factory.Faker('name')

    class Meta:
        model = models.FormFieldTemplate


class FormFieldFactory(factory.django.DjangoModelFactory):
    form = factory.SubFactory(FormFactory)
    template = factory.SubFactory(FormFieldTemplateFactory)

    class Meta:
        model = models.FormField


class FormSubmissionFactory(factory.django.DjangoModelFactory):
    form = factory.SubFactory(FormFactory)

    class Meta:
        model = models.FormSubmission


class APIUserFactory(factory.django.DjangoModelFactory):
    service_name = factory.Faker('company')

    class Meta:
        model = models.APIUser


class ExternalWebhookFactory(factory.django.DjangoModelFactory):
    form = factory.SubFactory(FormFactory)

    class Meta:
        model = models.ExternalWebhook