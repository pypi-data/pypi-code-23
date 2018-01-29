from openpyxl.formatting import Rule
from openpyxl.styles import Font
from openpyxl.styles.differential import DifferentialStyle
from openpyxl_templates.table_sheet.columns import ChoiceColumn, TextColumn, CharColumn

from django_ontology.api.importer import OntologyApiActions


class ActionColumn(ChoiceColumn):
    def __init__(self):
        super().__init__(
            default=OntologyApiActions.noop,
            choices=tuple((action, str(action)) for action in OntologyApiActions),
            width=10
        )

    def get_value_from_object(self, obj):
        return self.default


class ExpressionColumn(TextColumn):
    expression_type = None
    clear_command = "__clear__"  # TODO: Convert to setting

    def __init__(self, **kwargs):
        if "width" not in kwargs:
            kwargs["width"] = 40
        super().__init__(
            default=OntologyApiActions.noop,
            **kwargs
        )

    def get_value_from_object(self, obj):
        return getattr(obj, self.expression_type.type).raw

    def from_excel(self, cell, value):
        internal = super().from_excel(cell, value)
        if internal == self.clear_command:
            return None
        return internal

    def _to_excel(self, value):
        return str(value) if value is not OntologyApiActions.noop else ""

    def __str__(self):
        return "%s(%s)" % (self.__class__.__name__, self.expression_type)


class KeyColumn(CharColumn):
    def __init__(self):
        super().__init__(allow_blank=False, freeze=True, width=20)

        rule = Rule(
            type='expression',
            dxf=DifferentialStyle(
                font=Font(color='AAAAAA'),
            ),
            formula=["OR($D3, $F3)"]
        )

        self.conditional_formatting = rule


class ParentColumn(TextColumn):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        rule = Rule(
            type='expression',
            dxf=DifferentialStyle(
                font=Font(color='AAAAAA'),
            ),
            formula=["$E3"]
        )

        self.conditional_formatting = rule

    def get_value_from_object(self, obj):
        return obj.parent_id

    def prepare_worksheet(self, worksheet):
        super().prepare_worksheet(worksheet)