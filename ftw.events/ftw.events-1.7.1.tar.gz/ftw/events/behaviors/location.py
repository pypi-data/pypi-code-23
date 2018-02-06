from ftw.events import _
from plone.directives.form import IFormFieldProvider
from plone.directives.form import Schema
from zope.interface import alsoProvides
from zope.schema import TextLine


class ILocationFields(Schema):

    location_title = TextLine(
        title=_(
            u'label_location_title',
            default=u'Location: title'
        ),
        required=False,
        default=None,
    )

    location_street = TextLine(
        title=_(
            u'label_location_street',
            default=u'Location: street and number'
        ),
        required=False,
        default=None,
    )

    location_zip = TextLine(
        title=_(
            u'label_location_zip',
            default=u'Location: ZIP code'
        ),
        required=False,
        default=None,
    )

    location_city = TextLine(
        title=_(
            u'label_location_city',
            default=u'Location: city'
        ),
        required=False,
        default=None,
    )

alsoProvides(ILocationFields, IFormFieldProvider)
