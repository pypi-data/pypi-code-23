from ftw.events.behaviors.location import ILocationFields
from ftw.events.interfaces import IEventPage
from plone.app.event.dx.behaviors import IEventBasic
from plone.app.event.dx.behaviors import IEventLocation
from plone.autoform.interfaces import IFormFieldProvider
from plone.dexterity.content import Container
from plone.directives import form
from plone.supermodel.interfaces import FIELDSETS_KEY
from zope.interface import alsoProvides
from zope.interface import implements


# Move plone.app.event's default field "timezone" to the default schema,
# since all other fields are in the default schema and we do not want
# an extra schema only for the "timezone" field.
for fieldset in IEventBasic.queryTaggedValue(FIELDSETS_KEY, []):
    if 'timezone' in fieldset.fields:
        fieldset.fields.remove('timezone')


class IEventPageSchema(form.Schema):
    pass

alsoProvides(IEventPageSchema, IFormFieldProvider)


class EventPage(Container):
    implements(IEventPage)

    @property
    def location(self):
        if ILocationFields.providedBy(self):
            storage = ILocationFields(self)
            return ', '.join(filter(None, (
                storage.location_title,
                storage.location_street,
                ' '.join((storage.location_zip or '',
                          storage.location_city or '')).strip(),
            ))) or ''

        elif IEventLocation.providedBy(self):
            return vars(IEventLocation(self)).get('location', None)

        else:
            return None
