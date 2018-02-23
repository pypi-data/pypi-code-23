# -*- coding: utf-8 -*-
from collective.z3cform.datagridfield import DataGridFieldFactory
from collective.z3cform.datagridfield import DictRow
from collective.z3cform.datetimewidget import DateFieldWidget
from interlegis.portalmodelo.pl import _
from interlegis.portalmodelo.pl.config import START_REPUBLIC_BRAZIL, MIN_BIRTHDAY, MAX_BIRTHDAY
from interlegis.portalmodelo.pl.validators import check_birthday
from plone.app.z3cform.wysiwyg import WysiwygFieldWidget
from plone.autoform import directives as form
from plone.formwidget.contenttree import ObjPathSourceBinder
from plone.formwidget.datetime.z3cform import DateWidget
from plone.namedfile.field import NamedBlobImage
from plone.supermodel import model
from z3c.relationfield.schema import RelationChoice
from z3c.relationfield.schema import RelationList
from zope import schema
from zope.interface import Interface
from z3c.form.interfaces import IFieldWidget
from z3c.form.widget import FieldWidget
from zope.interface import implementer


class IBrowserLayer(Interface):
    """Add-on specific layer."""


class ISAPLMenuItem(Interface):
    """Marker interface to add a menu item on the display menu."""


@implementer(IFieldWidget)
def DateFieldWidget(field, request):
    widget = FieldWidget(field, DateWidget(request))
    widget.years_range = (-100, 10)
    widget.update()
    return widget


# TODO: validate date_affiliation < date_disaffiliation
class IPartyAffiliationItem(model.Schema):
    """Define a party affiliation record."""

    party = schema.TextLine(
        title=_(u'Party'),
        required=True,
    )

    form.widget(date_affiliation=DateFieldWidget)
    date_affiliation = schema.Date(
        title=_(u'Date of affiliation'),
        min=START_REPUBLIC_BRAZIL,
        required=True,
    )

    form.widget(date_disaffiliation=DateFieldWidget)
    date_disaffiliation = schema.Date(
        title=_(u'Date of disaffiliation'),
        min=START_REPUBLIC_BRAZIL,
        required=False,
    )


class IParliamentarian(model.Schema):
    """Represents a parliamentarian."""

    title = schema.TextLine(
        title=_(u'Name'),
        description=_(u''),
        required=True,
    )

    full_name = schema.TextLine(
        title=_(u'Full Name'),
        description=_(u''),
        required=True,
    )

    form.widget(birthday=DateFieldWidget)
    birthday = schema.Date(
        title=_(u'Birthday'),
        constraint=check_birthday,
        required=True,
        min=MIN_BIRTHDAY,
        max=MAX_BIRTHDAY,
    )

    form.widget(description=WysiwygFieldWidget)
    description = schema.Text(
        title=_(u'Bio'),
        description=_(u''),
        required=False,
    )

    image = NamedBlobImage(
        title=_(u'Portrait'),
        description=_(u''),
        required=False,
    )

    email = schema.TextLine(
        title=_(u'E-mail'),
        description=_(u''),
        required=False,
    )

    site = schema.TextLine(
        title=_(u'Site'),
        description=_(u''),
        required=False,
    )

    address = schema.TextLine(
        title=_(u'Address'),
        description=_(u''),
        required=True,
    )

    postal_code = schema.TextLine(
        title=_(u'Postal code'),
        description=_(u''),
        required=True,
    )

    telephone = schema.ASCIILine(
        title=_(u'Telephone'),
        description=_(u''),
        required=True,
    )

    form.widget(party_affiliation=DataGridFieldFactory)
    party_affiliation = schema.List(
        title=_(u'Party affiliation'),
        description=_(u''),
        required=True,
        value_type=DictRow(title=u'party_affiliation_row', schema=IPartyAffiliationItem),
        default=[],
    )


class ILegislature(model.Schema):
    """Represents a legislature."""

    title = schema.TextLine(
        title=_(u'Number'),
        description=_(u''),
        required=True,
    )

    description = schema.Text(
        title=_(u'Description'),
        description=_(u''),
        required=False,
    )

    start_date = schema.Date(
        title=_(u'Start date'),
        description=_(u''),
        required=True,
    )

    end_date = schema.Date(
        title=_(u'End date'),
        description=_(u''),
        required=True,
    )

    members = RelationList(
        title=_(u'Members'),
        required=False,
        default=[],
        value_type=RelationChoice(
            title=_(u'Members'),
            source=ObjPathSourceBinder(object_provides=IParliamentarian.__identifier__),
        ),
    )


class IBoardMember(model.Schema):
    """Define a board member record."""

    # XXX: this should be the right way to do it but we have an issue
    #      involving at least 2 packages: plone.formwidget.contenttree
    #      and zope.pagetemplate
    #      see: https://stackoverflow.com/questions/22769633/using-relations-in-a-datagridfield
    # member = RelationChoice(
    #     title=_(u'Member'),
    #     required=True,
    #     source=ObjPathSourceBinder(object_provides=IParliamentarian.__identifier__),
    # )

    member = schema.TextLine(
        title=_(u'Member'),
        required=True,
    )

    position = schema.TextLine(
        title=_(u'Position'),
        required=True,
    )


class ISession(model.Schema):
    """Represents a legislative session."""

    title = schema.TextLine(
        title=_(u'Number'),
        description=_(u''),
        required=True,
    )

    description = schema.Text(
        title=_(u'Description'),
        description=_(u''),
        required=False,
    )

    start_date = schema.Date(
        title=_(u'Start date'),
        description=_(u''),
        required=True,
    )

    end_date = schema.Date(
        title=_(u'End date'),
        description=_(u''),
        required=True,
    )

    form.widget(legislative_board=DataGridFieldFactory)
    legislative_board = schema.List(
        title=_(u'Legislative Board'),
        description=_(u''),
        required=False,
        value_type=DictRow(title=u'legislative_board_row', schema=IBoardMember),
        default=[],
    )

