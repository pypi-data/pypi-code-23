# encoding: utf-8
from AccessControl import ClassSecurityInfo
from Products.Archetypes.Registry import registerWidget
from Products.Archetypes.Widget import TypesWidget
from collective.archetypes.select2.base import SelectWidget
from collective.archetypes.select2.utils import NotImplemented


class BaseWidget(TypesWidget):
    """Base widget for Archetypes."""

    _properties = TypesWidget._properties.copy()
    _properties.update({
        'macro': 'patterns_widget',
        'pattern': None,
        'pattern_options': {},
    })

    def _base(self, pattern, pattern_options={}):
        """Base widget class."""
        raise NotImplemented

    def _base_args(self, context, field, request):
        """Method which will calculate _base class arguments.

        Returns (as python dictionary):
            - `pattern`: pattern name
            - `pattern_options`: pattern options

        :param context: Instance of content type.
        :type context: context

        :param request: Request object.
        :type request: request

        :param field: Instance of field of this widget.
        :type field: field

        :returns: Arguments which will be passed to _base
        :rtype: dict
        """
        if self.pattern is None:
            raise NotImplemented("'pattern' option is not provided.")
        return {
            'pattern': self.pattern,
            'pattern_options': self.pattern_options,
        }

    def view(self, context, field, request):
        """Render widget on view.

        :returns: Fields value.
        :rtype: string
        """
        return field.getAccessor(context)()

    def edit(self, context, field, request):
        """Render widget on edit.

        :returns: Widget's HTML.
        :rtype: string
        """
        return self._base(**self._base_args(context, field, request)).render()


class Select2Widget(BaseWidget):
    """Select widget for Archetypes."""

    _base = SelectWidget

    _properties = BaseWidget._properties.copy()
    _properties.update({
        'pattern': 'select2',
        'pattern_options': {},
        'separator': ';',
        'multiple': False,
        'orderable': False,
    })

    def _base_args(self, context, field, request):
        """Method which will calculate _base class arguments.

        Returns (as python dictionary):
            - `pattern`: pattern name
            - `pattern_options`: pattern options
            - `name`: field name
            - `value`: field value
            - `multiple`: field multiple
            - `items`: field items from which we can select to

        :returns: Arguments which will be passed to _base
        :rtype: dict
        """
        args = super(Select2Widget, self)._base_args(context, field, request)
        args['name'] = field.getName()
        args['value'] = (request.get(field.getName(),
                                     field.getAccessor(context)()))
        args['multiple'] = self.multiple

        items = []
        for item in field.Vocabulary(context).items():
            items.append((item[0], item[1]))
        args['items'] = items

        args.setdefault('pattern_options', {})

        if self.separator:
            args['pattern_options']['separator'] = self.separator

        if self.multiple and self.orderable:
            args['pattern_options']['orderable'] = True

        return args

    security = ClassSecurityInfo()
    security.declarePublic('process_form')

    def process_form(self, instance, field, form, empty_marker=None):
        value = form.get(field.getName(), empty_marker)
        if value is empty_marker:
            return empty_marker, {}
        if self.multiple and isinstance(value, basestring):
            value = value.strip().split(self.separator)
        return value, {}


class MultiSelect2Widget(Select2Widget):

    _properties = Select2Widget._properties.copy()
    _properties.update({
        'pattern': 'select2',
        'pattern_options': {},
        'separator': ';',
        'multiple': True,
        'orderable': False,
    })


registerWidget(
    Select2Widget,
    title='Select2 widget',
    description=('Select2 widget'),
    used_for=('Products.Archetypes.Field.SelectField',)
)


registerWidget(
    MultiSelect2Widget,
    title='Muli Select2 widget',
    description=('Multi Select2 widget'),
    used_for=('Products.Archetypes.Field.LinesField',)
)
