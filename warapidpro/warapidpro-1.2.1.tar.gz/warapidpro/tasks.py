import requests
import json
import urllib
from datetime import datetime, timedelta
from temba import celery_app
from dateutil import parser
from django.conf import settings
from django.utils import timezone
from django.db.models import Q
from warapidpro.types import (
    WhatsAppDirectType, WhatsAppGroupType, WHATSAPP_CHANNEL_TYPES)
from warapidpro.views import DEFAULT_AUTH_URL


@celery_app.task
def refresh_channel_auth_token(channel_pk):
    from temba.channels.models import Channel

    channel = Channel.objects.get(pk=channel_pk)
    config = channel.config_json()
    authorization = config['authorization']

    wassup_url = getattr(
        settings, 'WASSUP_AUTH_URL', DEFAULT_AUTH_URL)
    client_id = getattr(
        settings, 'WASSUP_AUTH_CLIENT_ID', None)
    client_secret = getattr(
        settings, 'WASSUP_AUTH_CLIENT_SECRET', None)

    response = requests.post(
        '%s/oauth/token/' % (wassup_url,),
        {
            "grant_type": "refresh_token",
            "refresh_token": authorization['refresh_token'],
            "client_id": client_id,
            "client_secret": client_secret,
        },
        {
            "content-type": "application/x-www-form-urlencoded",
            "accept": "application/json",
        })
    response.raise_for_status()
    new_authorization = response.json()

    config.update({
        'authorization': new_authorization,
        'expires_at': (
            datetime.now() + timedelta(
                seconds=new_authorization['expires_in'])).isoformat(),
    })

    channel.config = json.dumps(config)
    channel.save()


@celery_app.task
def refresh_channel_auth_tokens(delta=timedelta(minutes=5)):
    from temba.channels.models import Channel
    channels = Channel.objects.filter(
        Q(channel_type=WhatsAppDirectType.code) |
        Q(channel_type=WhatsAppGroupType.code))
    for channel in channels:
        config = channel.config_json()
        # This is for integrations that are pre-oauth
        # and which use an api_token which doesn't expire
        if 'expires_at' not in config:
            continue
        expires_at = parser.parse(config['expires_at'])
        marker = datetime.now() + delta
        if marker > expires_at:
            refresh_channel_auth_token.delay(channel.pk)


@celery_app.task
def check_org_whatsappable(org, sample_size=100):
    from warapidpro.models import (
        has_whatsapp_contactfield, has_whatsapp_timestamp_contactfield)
    from temba.contacts.models import Contact

    channels = org.channels.filter(
        channel_type__in=WHATSAPP_CHANNEL_TYPES, is_active=True)
    if not channels.exists():
        return

    channel = channels.order_by('-modified_on').first()

    has_whatsapp = has_whatsapp_contactfield(org)
    has_whatsapp_timestamp = has_whatsapp_timestamp_contactfield(org)

    all_contacts = Contact.objects.filter(org=org)
    new_contacts = all_contacts.exclude(
        Q(values__contact_field=has_whatsapp) |
        Q(values__contact_field=has_whatsapp_timestamp))

    for contact in new_contacts.order_by('?')[:sample_size]:
        check_contact_whatsappable.delay(contact.pk, channel.pk)


@celery_app.task
def refresh_org_whatsappable(org, sample_size=100, delta=timedelta(days=7)):
    from warapidpro.models import (
        has_whatsapp_contactfield, has_whatsapp_timestamp_contactfield)
    from temba.contacts.models import Contact

    channels = org.channels.filter(
        channel_type__in=WHATSAPP_CHANNEL_TYPES, is_active=True)
    if not channels.exists():
        return

    channel = channels.order_by('-modified_on').first()

    has_whatsapp = has_whatsapp_contactfield(org)
    has_whatsapp_timestamp = has_whatsapp_timestamp_contactfield(org)

    checked_before = Contact.objects.filter(
        org=org, values__contact_field=has_whatsapp)

    needing_refreshing = checked_before.filter(
        values__contact_field=has_whatsapp_timestamp,
        values__datetime_value__lte=timezone.now() - delta)

    for contact in needing_refreshing.order_by('?')[:sample_size]:
        check_contact_whatsappable.delay(contact.pk, channel.pk)


@celery_app.task
def check_contact_whatsappable(contact_pk, channel_pk):
    from warapidpro.models import (
        has_whatsapp_contactfield, has_whatsapp_timestamp_contactfield,
        get_whatsappable_group, YES, NO)
    from temba.contacts.models import Contact, TEL_SCHEME
    from temba.channels.models import Channel

    contact = Contact.objects.get(pk=contact_pk)
    org = contact.org
    urn = contact.get_urn(TEL_SCHEME)
    channel = Channel.objects.get(pk=channel_pk)

    has_whatsapp = has_whatsapp_contactfield(org)
    has_whatsapp_timestamp = has_whatsapp_timestamp_contactfield(org)

    # Make sure the group exists
    get_whatsappable_group(org)

    config = channel.config_json()
    authorization = config.get('authorization', {})
    token = authorization.get('access_token') or config.get('api_token')

    response = requests.get(
        'https://wassup.p16n.org/api/v1/numbers/check/?%s' % (
            urllib.urlencode({
                "number": channel.address,
                "address": urn.path,
                "wait": "true",
            }),),
        headers={'Authorization': '%s %s' % (
            authorization.get('token_type', 'Token'),
            token,
        )})

    response.raise_for_status()
    payload = response.json().get(channel.address)
    has_whatsapp_value = YES if payload.get('exists') is True else NO
    contact.set_field(
        user=org.administrators.first(),
        key=has_whatsapp.key, value=has_whatsapp_value)
    contact.set_field(
        user=org.administrators.first(),
        key=has_whatsapp_timestamp.key, value=timezone.now())
