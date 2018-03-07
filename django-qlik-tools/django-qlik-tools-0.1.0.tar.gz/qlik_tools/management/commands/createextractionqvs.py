from django.apps import apps
from django.core.management.base import BaseCommand, CommandError
from django.utils.text import capfirst


TEMPLATE_LOAD_TABLE = """[{model}]:
LOAD *;
SQL SELECT
{fields}
FROM {db_table};

"""

TEMPLATE_LOAD_CHOICES_INLINE = """LEFT JOIN ({model})
LOAD * INLINE [{field}_choice_value, {field}
{values}];

"""


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('app', nargs='+', type=str)
        parser.add_argument('--model', action='store', dest='model', default=None)

    def handle(self, *args, **options):
        script = ''
        for app_name in options['app']:
            app = apps.get_app_config(app_name)

            if options['model']:
                models = (app.get_model(options['model']),)
            else:
                models = app.get_models()

            for model in models:
                load_table_statement = self.get_load_table_statement(model)
                load_choices_inline_statement = self.load_choices_inline_statement(model)

                script += load_table_statement
                if load_choices_inline_statement:
                    script += load_choices_inline_statement
                script += 'STORE {model} into [qvd\{model}.qvd];\n'.format(model=model._meta.model_name)
                script += 'DROP Table {};\n\n'.format(model._meta.model_name)

        return script

    def get_load_table_statement(self, model):
        fields = [self.get_field_name(field)
            for field
            in model._meta.get_fields()
            if hasattr(field, 'get_attname_column')]

        return TEMPLATE_LOAD_TABLE.format(
            model=model._meta.model_name,
            fields=',\n'.join(fields),
            db_table=model._meta.db_table)

    def get_field_name(self, field):
        name = field.get_attname_column()[1]
        if hasattr(field, 'choices') and field.choices:
            name += ' as {}_choice_value'.format(name)

        return name

    def load_choices_inline_statement(self, model):
        script = ''

        fields_with_choices = [field
            for field
            in model._meta.get_fields()
            if hasattr(field, 'choices') and field.choices]

        for field in fields_with_choices:
            choices = ['{}, {}'.format(choice[0], choice[1])
                for choice
                in field.choices]

            script += TEMPLATE_LOAD_CHOICES_INLINE.format(
                model=model._meta.model_name,
                field=field.name,
                values='\n'.join(choices))

        return script
