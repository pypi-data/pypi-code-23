# -*- coding: utf-8 -*-
from genomix.fields import DisplayChoiceField
from rest_framework import serializers

from . import choices, models


class TermSerializer(serializers.ModelSerializer):
    """Serializer for HPO Terms."""

    version = serializers.StringRelatedField()

    class Meta:
        model = models.Term
        fields = (
            'id', 'version', 'hpo_term', 'label', 'description',
            'hpo_url',
            'created_by', 'created', 'modified',
        )


class SynonymSerializer(serializers.ModelSerializer):
    """Serializer for HPO Term Synonms."""

    hpo_term = serializers.StringRelatedField()
    scope = DisplayChoiceField(choices=choices.SYNONYM_SCOPES)

    class Meta:
        model = models.Term
        fields = (
            'id', 'hpo_term', 'description', 'scope',
            'created', 'modified',
        )


class CrossReferenceSerializer(serializers.ModelSerializer):
    """Serializer for HPO Term Cross References."""

    hpo_term = serializers.StringRelatedField()
    source = DisplayChoiceField(choices=choices.CROSS_REFERENCES)

    class Meta:
        model = models.CrossReference
        fields = (
            'id', 'hpo_term', 'source', 'source_value',
            'created', 'modified',
        )


class DiseaseSerializer(serializers.ModelSerializer):
    """Serializer for Diseases."""

    version = serializers.StringRelatedField()
    database = DisplayChoiceField(choices=choices.DATABASES)
    qualifier = DisplayChoiceField(choices=choices.QUALIFIERS)
    evidence_code = DisplayChoiceField(choices=choices.EVIDENCE)
    mode_of_inheritance = TermSerializer(read_only=True)
    age_of_onset = TermSerializer(read_only=True)
    frequency = TermSerializer(read_only=True)
    hpo_terms = serializers.SerializerMethodField()
    genes = serializers.StringRelatedField(many=True)

    class Meta:
        model = models.Disease
        fields = (
            'id', 'version', 'database', 'identifier', 'description', 'database_url',
            'qualifier', 'evidence_code',
            'mode_of_inheritance', 'age_of_onset', 'frequency',
            'hpo_terms', 'genes',
            'create_date', 'assigned_by',
            'created', 'modified',
        )

    def get_hpo_terms(self, obj):
        return ['{0} - {1}'.format(x.hpo_term, x.label) for x in obj.hpo_terms.all()]
