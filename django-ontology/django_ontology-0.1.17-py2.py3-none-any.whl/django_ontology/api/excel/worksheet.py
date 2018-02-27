from openpyxl_templates.table_sheet import TableSheet, OrderedDict
from openpyxl_templates.table_sheet.columns import CharColumn, BoolColumn, DateColumn

from django_ontology.api.excel.columns import ActionColumn, ParentColumn, ExpressionColumn, KeyColumn
from django_ontology.api.importer import ApiRow


class OntologySheet(TableSheet):
    model = None

    action = ActionColumn()
    key = KeyColumn()
    parent = ParentColumn(allow_blank=True, width=20)
    static = BoolColumn(hidden=True)
    static_parent = BoolColumn(hidden=True)
    used_in_template = BoolColumn(hidden=True)
    created = DateColumn(group=True, hidden=True)
    modified = DateColumn(group=True, hidden=True)

    _class_registry = {}

    def __init__(self, language, *args,  **kwargs):
        self.language = language
        super().__init__(*args, **kwargs)

    @classmethod
    def from_model(cls, model):
        if model not in cls._class_registry:
            classdict = OrderedDict((
                ("model", model),
                ("row_class", ApiRow.from_model(model))
            ))

            for expression_type in model.expression_types:
                column = expression_type.excel_column or ExpressionColumn()
                column.expression_type = expression_type
                classdict[expression_type.type] = column

            cls._class_registry[model] = type(
                "%sSheet" % model.__name__,
                (cls, ),
                classdict
            )

        return cls._class_registry[model]

