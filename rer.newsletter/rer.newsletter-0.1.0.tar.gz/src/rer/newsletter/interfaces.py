# -*- coding: utf-8 -*-
from plone import schema
from plone.app.textfield import RichText as RichTextField
from plone.app.z3cform.widget import RichTextFieldWidget
from plone.autoform import directives as form
from plone.supermodel import model
from rer.newsletter import _
from zope.interface import Interface
from zope.publisher.interfaces.browser import IDefaultBrowserLayer

import uuid


def default_id_channel():
    return unicode(uuid.uuid4())


class IRerNewsletterLayer(IDefaultBrowserLayer):
    """Marker interface that defines a browser layer."""


class IChannel(Interface):
    """Marker interface that define a channel of newsletter"""


class IChannelSchema(model.Schema):
    """a dexterity schema for channel of newsletter"""

    sender_name = schema.TextLine(
        title=_(u'sender_name', default=u'Sender Fullname'),
        description=_(u'description_sender_name',
                      default=u'Fullname of sender'),
        required=False,
    )

    sender_email = schema.Email(
        title=_(u'sender_email', default=u'Sender email'),
        description=_(u'description_sender_email',
                      default=u'Email of sender'),
        required=True,
    )

    subject_email = schema.TextLine(
        title=_(u'subject_email', default=u'Subject email'),
        description=_(u'description_subject_mail',
                      default=u'Subject for channel message'),
        required=False
    )

    response_email = schema.Email(
        title=_(u'response_email', default=u'Response email'),
        description=_(u'description_response_email',
                      default=u'Response email of channel'),
        required=False,
    )

    privacy = RichTextField(
        title=_(u'privacy_channel', default=u'Informativa sulla privacy'),
        description=_(u'description_privacy_channel',
                      default=u'Informativa sulla privacy per questo canale'),
        required=False,
        default=u'',
    )
    form.widget('privacy', RichTextFieldWidget)

    header = RichTextField(
        title=_(u'header_channel', default=u'Header of message'),
        description=_(u'description_header_channel',
                      default=u'Header for message of this channel'),
        required=False,
        default=u'',
    )
    form.widget('header', RichTextFieldWidget)

    footer = RichTextField(
        title=_(u'footer_channel', default=u'Footer of message'),
        description=_(u'description_footer_channel',
                      default=u'Footer for message of this channel'),
        required=False,
        default=u'',
    )
    form.widget('footer', RichTextFieldWidget)

    css_style = schema.Text(
        title=_(u'css_style', default=u'CSS Style'),
        description=_(u'description_css_style', default=u'style for mail'),
        required=False,
        default=u'',
    )

    # probabilemente un campo che va nascosto
    id_channel = schema.TextLine(
        title=_(u'idChannel', default=u'Channel ID'),
        description=_(u'description_IDChannel', default=u'Channel ID'),
        required=True,
        defaultFactory=default_id_channel,
    )

    is_subscribable = schema.Bool(
        title=_(u'is_subscribable', default=u'Is Subscribable'),
        default=False,
        required=False
    )


class IMessage(Interface):
    """Marker interface that define a message"""


class IMessageSchema(model.Schema):
    """a dexterity schema for message"""
