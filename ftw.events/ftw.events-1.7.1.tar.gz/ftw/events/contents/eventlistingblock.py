from Acquisition import aq_inner, aq_parent
from ftw.events import _
from ftw.events.interfaces import IEventListingBlock
from ftw.keywordwidget.widget import KeywordFieldWidget
from ftw.referencewidget.sources import DefaultSelectable
from ftw.referencewidget.sources import ReferenceObjSourceBinder
from ftw.referencewidget.widget import ReferenceWidgetFactory
from ftw.simplelayout.contenttypes.behaviors import IHiddenBlock
from plone import api
from plone.autoform import directives
from plone.autoform.interfaces import IFormFieldProvider
from plone.dexterity.content import Item
from plone.directives import form
from plone.uuid.interfaces import IUUID
from Products.CMFPlone.interfaces.syndication import IFeedSettings
from Products.CMFPlone.interfaces.syndication import ISyndicatable
from z3c.relationfield import RelationChoice
from zope import schema
from zope.interface import alsoProvides
from zope.interface import implements
from zope.interface import invariant, Invalid


class FilterByPathSelectable(DefaultSelectable):

    def is_selectable(self):
        """ Allow to reference any path"""
        return True


class IEventListingBlockSchema(form.Schema):
    form.fieldset(
        'filter',
        label=_(u'event_listing_fieldset_filter_label',
                default=u'Filter'),
        fields=[
            'filter_by_path',
            'current_context',
            'subjects',
        ]
    )

    form.fieldset(
        'link',
        label=_(u'event_listing_fieldset_link_label',
                default=u'Link'),
        fields=[
            'show_more_items_link',
            'more_items_link_label',
            'more_items_view_title',
        ]
    )

    form.fieldset(
        'advanced',
        label=_(u'event_listing_fieldset_advanced_label',
                default=u'Advanced'),
        fields=[
            'exclude_past_events',
            'hide_empty_block',
        ]
    )

    title = schema.TextLine(
        title=_(u'event_listing_config_title_label', default=u'Title'),
        description=u'',
        required=True,
        default=u'',
    )

    show_title = schema.Bool(
        title=_(u'event_listing_block_show_title_label', default=u'Show title'),
        default=True,
        required=False,
    )

    exclude_past_events = schema.Bool(
        title=_(u'label_exclude_past_events', default=u'Exclude past events'),
        default=True,
        required=False,
    )

    form.widget(filter_by_path=ReferenceWidgetFactory)
    filter_by_path = schema.List(
        title=_(u'event_listing_config_filter_path_label',
                default=u'Limit to path'),
        description=_(u'event_listing_config_filter_path_description',
                      default=u'Only show content from a specific path.'),
        value_type=RelationChoice(
            source=ReferenceObjSourceBinder(
                selectable_class=FilterByPathSelectable),
        ),
        required=False,
        default=[],
        missing_value=[],
    )

    current_context = schema.Bool(
        title=_(u'event_listing_config_filter_current_context_label',
                default=u'Limit to current context'),
        description=_(
            u'event_listing_config_filter_current_context_description',
            default=u'Only show items from the current context.'),
        default=True,
    )

    quantity = schema.Int(
        title=_(u'event_listing_config_quantity_label', default=u'Quantity'),
        description=_(u'event_listing_config_quantity_description',
                      default=u'The number of items to be shown at most. '
                              u'Enter 0 for no limitation.'),
        default=5,
    )

    directives.widget('subjects', KeywordFieldWidget)
    subjects = schema.List(
        title=_(u'event_listing_config_subjects_label',
                default=u'Filter by subject'),
        description=_(u'event_listing_config_subjects_description',
                      default=u'Only items with the selected subjects will '
                              u'be shown.'),
        value_type=schema.Choice(vocabulary='ftw.events.vocabulary.subjects'),
        required=False,
        default=[],
        missing_value=[],
    )

    show_description = schema.Bool(
        title=_(u'event_listing_config_show_description_label',
                default=u'Show the description of the item'),
        default=True,
    )

    description_length = schema.Int(
        title=_(u'event_listing_config_description_length_label',
                default=u'Length of the description'),
        description=_(u'event_listing_config_description_length_description',
                      default=u'The maximum length of the item\'s '
                              u'description. Longer descriptions will be '
                              u'cropped. Enter 0 for no limitation.'),
        default=50,
    )

    show_more_items_link = schema.Bool(
        title=_(u'event_listing_config_show_more_items_link',
                default=u'Show link to more items'),
        description=_(u'event_listing_show_more_items_link_description',
                      default=u'Render a link to a page which renders more '
                              u'items (only if there is at least one item).'),
        default=False,
    )

    more_items_link_label = schema.TextLine(
        title=_(u'label_more_items_link_label',
                default=u'Label for the "more items" link'),
        description=_(u'description_more_items_link_label',
                      default=u'This custom label will not be translated.'),
        required=False,
    )

    more_items_view_title = schema.TextLine(
        title=_(u'label_more_items_view_title',
                default=u'Title of the view behind the "more items" link'),
        description=_(u'description_more_items_view_title',
                      default=u'This title will not be translated.'),
        required=False,
    )

    show_rss_link = schema.Bool(
        title=_(u'label_show_rss_link',
                default=u'Link to RSS feed'),
        description=_(u'description_show_rss_link',
                      default=u'Render a link to the RSS feed of the events.'),
        default=False,
        required=False,
    )

    hide_empty_block = schema.Bool(
        title=_(u'label_hide_empty_block',
                default=u'Hide empty block'),
        description=_(u'description_hide_empty_block',
                      default=u'Hide the block if there are not events to be shown.'),
        default=False,
        required=False,
    )

    @invariant
    def is_either_path_or_context(obj):
        """Checks if not both path and current context are defined.
        """
        if obj.current_context and obj.filter_by_path:
            raise Invalid(_(
                u'event_listing_config_current_context_and_path_error',
                default=u'You cannot filter by path and current context '
                        u'at the same time.')
            )

alsoProvides(IEventListingBlockSchema, IFormFieldProvider)


class EventListingBlock(Item):
    implements(IEventListingBlock, ISyndicatable, IHiddenBlock)

    @property
    def is_hidden(self):
        if not self.hide_empty_block:
            return False

        # For unknown reason, `self` is not acquisition wrapped. We
        # need to get an acquisition wrapped event listing block we
        # work with.
        obj = api.content.get(UID=IUUID(self))

        if self.user_can_edit_block(obj):
            # Editors must always see the block or they cannot edit it anymore.
            return True

        items = api.content.get_view(
            name='block_view', context=obj, request=obj.REQUEST
        ).get_items()
        return self.hide_empty_block and not items

    @is_hidden.setter
    def is_hidden(self, value):
        """
        This is a dummy setter method in case somebody activates the IHiddenBlock
        behavior from ftw.simplelayout on the event listing block which makes no
        sense. It should not be a use case to allow hiding event listing blocks
        because the block does not really contain the objects, it only displays
        them from a different location. So if an event listing block ist not desired
        it should be removed from the content page instead.
        """
        raise Exception(
            'You are not allowed to add the IHiddenBlock behavior on the event listing block.'
        )

    def user_can_edit_block(self, obj):
        container = aq_parent(aq_inner(obj))
        return api.user.has_permission(
            'Modify portal content',
            obj=container,
        )


def enable_syndication(event_listing_block, event=None):
    """
    Enables syndication on the given event listing block. This
    must be called from a subscriber when an event listing block is
    created so the syndication is enabled by default on the event
    listing blocks.
    """
    settings = IFeedSettings(event_listing_block)
    settings.enabled = True
    settings.feed_types = ('RSS', 'rss.xml', 'atom.xml')
