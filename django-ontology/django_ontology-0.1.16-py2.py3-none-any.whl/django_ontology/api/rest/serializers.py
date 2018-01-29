from collections import OrderedDict

from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework_recursive.fields import RecursiveField

from django_ontology.api.importer import ApiRow, OntologyApiActions, OntologyImporter


class FormattedExpressionField(serializers.CharField):
    def __init__(self, model_field, **kwargs):
        super().__init__(
            allow_null=True,
            allow_blank=True,
            read_only=False,
            required=False,
            **kwargs)
        self.model_field = model_field

    def to_representation(self, value):
        return OrderedDict((
            ("raw", value.raw or ""),
            ("formatted", value.formatted or "")
        ))

    def to_internal_value(self, data):
        if not isinstance(data, dict):
            raise ValueError("Unknown data type")

        return data["raw"]


class UnformattedExpressionField(FormattedExpressionField):
    def to_representation(self, value):
        return value.raw or ""

    def to_internal_value(self, data):
        return data


class RestSerializer(serializers.Serializer):
    _class_registry = {}

    key = serializers.CharField(allow_blank=True, allow_null=False)
    parent = serializers.CharField(required=False, allow_blank=True, allow_null=True, source="parent_id")
    static = serializers.BooleanField(read_only=True)
    static_parent = serializers.BooleanField(read_only=True)
    used_in_template = serializers.BooleanField(read_only=True)
    children = serializers.ListField(child=RecursiveField(), source="get_children", read_only=True)

    def __init__(self, *args, language=None, **kwargs):
        self.language = language
        super().__init__(*args, **kwargs)

    def get_fields(self):
        fields = super().get_fields()
        fields.move_to_end("children")
        return fields

    @classmethod
    def from_model(cls, model):
        if model not in cls._class_registry:
            classdict = OrderedDict((("model", model),))
            for model_field in model.expression_types:
                classdict[model_field.type] = model_field.rest_serializer or (
                    FormattedExpressionField(model_field)
                    if model_field.is_formatted
                    else UnformattedExpressionField(model_field)
                )
            classdict.update(model.additional_rest_fields())
            cls._class_registry[model] = type(
                "%s%s" % (model.__name__, cls.__name__),
                (cls,),
                classdict
            )
        return cls._class_registry[model]

    def update(self, instance, validated_data):
        if "parent_id" in validated_data:
            validated_data["parent"] = validated_data["parent_id"] or None
            del validated_data["parent_id"]
        else:
            validated_data["parent"] = OntologyApiActions.noop

        if validated_data["key"] != instance.key:
            instance = instance.change_key(validated_data["key"])

        result = OntologyImporter(
            model=self.model,
            rows=[ApiRow(action=OntologyApiActions.update, **validated_data)],
            language=self.language,
            concepts=[instance]
        ).result

        if result.success:
            return self.model.translate.get(key=instance.key)
        else:
            raise ValidationError(result.exceptions)

    def create(self, validated_data):
        if "parent_id" in validated_data:
            validated_data["parent"] = validated_data["parent_id"]
            del validated_data["parent_id"]

        result = OntologyImporter(
            model=self.model,
            rows=[ApiRow(action=OntologyApiActions.create, **validated_data)],
            language=self.language,
            concepts=[]
        ).result
        if result.success:
            if result.create:
                instance = result.create[0]
            else:
                instance = result.update[0]

            return instance
        else:
            raise ValidationError(result.exceptions)

