# -*- coding: utf-8 -*-
from django import forms
from django.db.models import CharField, TextField, Q

import django_filters
from genome.models import Gene
from genome.choices import HGNC_GENE_STATUS
from genomix.filters import DisplayChoiceFilter

from . import choices, models, utils


class TermFilter(django_filters.rest_framework.FilterSet):

    hpo_term = django_filters.CharFilter(
        label='HPO Term',
        method='filter_hpo_term',
    )
    is_a = django_filters.ModelMultipleChoiceFilter(
        queryset=models.Term.objects.fast(),
        widget=django_filters.widgets.CSVWidget,
        help_text='Multiple values may be separated by commas.',
    )
    is_a_terms = django_filters.BaseCSVFilter(
        label='Is a terms',
        method='filter_is_a_terms',
        widget=django_filters.widgets.CSVWidget
    )
    can_be = django_filters.ModelMultipleChoiceFilter(
        queryset=models.Term.objects.fast(),
        widget=django_filters.widgets.CSVWidget,
        help_text='Multiple values may be separated by commas.',
    )
    can_be_terms = django_filters.BaseCSVFilter(
        label='Can be terms',
        method='filter_can_be_terms',
        widget=django_filters.widgets.CSVWidget
    )

    class Meta:
        model = models.Term
        fields = [
            'version',
            'version__label',
            'identifier',
            'label',
            'description',
            'is_a',
            'can_be',
            'diseases__description'
        ]
        filter_overrides = {
            CharField: {
                'filter_class': django_filters.CharFilter,
                'extra': lambda f: {
                    'lookup_expr': 'icontains',
                },
            },
            TextField: {
                'filter_class': django_filters.CharFilter,
                'extra': lambda f: {
                    'lookup_expr': 'icontains',
                },
            }
        }

    def filter_hpo_term(self, queryset, name, value):
        return queryset.hpo_term(hpo_term=value)

    def filter_is_a_terms(self, queryset, name, value):
        return queryset.is_a_terms(hpo_terms=value)

    def filter_can_be_terms(self, queryset, name, value):
        return queryset.can_be_terms(hpo_terms=value)


class CrossReferenceFilter(django_filters.rest_framework.FilterSet):

    hpo_term = django_filters.ModelChoiceFilter(
        queryset=models.Term.objects.fast(),
        widget=forms.NumberInput,
    )
    hpo_terms = django_filters.BaseCSVFilter(
        label='HPO Terms',
        method='filter_hpo_terms',
        widget=django_filters.widgets.CSVWidget
    )
    source = DisplayChoiceFilter(choices=choices.CROSS_REFERENCES)

    class Meta:
        model = models.CrossReference
        fields = [
            'hpo_term',
            'source',
            'source_value',
        ]
        filter_overrides = {
            CharField: {
                'filter_class': django_filters.CharFilter,
                'extra': lambda f: {
                    'lookup_expr': 'icontains',
                },
            }
        }

    def filter_hpo_terms(self, queryset, name, value):
        return queryset.hpo_terms(hpo_terms=value)


class DiseaseFilter(django_filters.rest_framework.FilterSet):

    database = DisplayChoiceFilter(choices=choices.DATABASES)
    qualifier = DisplayChoiceFilter(choices=choices.QUALIFIERS)
    evidence_code = DisplayChoiceFilter(choices=choices.EVIDENCE)
    mode_of_inheritance = django_filters.ModelMultipleChoiceFilter(
        queryset=models.Term.objects.fast(),
        widget=django_filters.widgets.CSVWidget,
        help_text='Multiple values may be separated by commas.',
    )
    mode_of_inheritance_terms = django_filters.BaseCSVFilter(
        label='Mode of inheritance terms',
        method='filter_mode_of_inheritance_terms',
        widget=django_filters.widgets.CSVWidget
    )
    age_of_onset = django_filters.ModelMultipleChoiceFilter(
        queryset=models.Term.objects.fast(),
        widget=django_filters.widgets.CSVWidget,
        help_text='Multiple values may be separated by commas.',
    )
    age_of_onset_terms = django_filters.BaseCSVFilter(
        label='Age of onsent terms',
        method='filter_age_of_onset_terms',
        widget=django_filters.widgets.CSVWidget
    )
    frequency = django_filters.ModelMultipleChoiceFilter(
        queryset=models.Term.objects.fast(),
        widget=django_filters.widgets.CSVWidget,
        help_text='Multiple values may be separated by commas.',
    )
    frequency_terms = django_filters.BaseCSVFilter(
        label='Frequency terms',
        method='filter_frequency_terms',
        widget=django_filters.widgets.CSVWidget
    )
    hpo_terms = django_filters.BaseCSVFilter(
        label='HPO Terms',
        method='filter_hpo_terms',
        widget=django_filters.widgets.CSVWidget
    )
    genes = django_filters.ModelMultipleChoiceFilter(
        queryset=Gene.objects.fast(),
        widget=django_filters.widgets.CSVWidget,
        help_text='Multiple values may be separated by commas.',
    )
    genes__symbol = django_filters.CharFilter(lookup_expr='iexact', distinct=True)

    class Meta:
        model = models.Disease
        fields = [
            'version',
            'version__label',
            'database',
            'identifier',
            'description',
            'qualifier',
            'evidence_code',
            'mode_of_inheritance',
            'age_of_onset',
            'frequency',
            'genes',
            'genes__symbol',
        ]
        filter_overrides = {
            CharField: {
                'filter_class': django_filters.CharFilter,
                'extra': lambda f: {
                    'lookup_expr': 'icontains',
                },
            },
            TextField: {
                'filter_class': django_filters.CharFilter,
                'extra': lambda f: {
                    'lookup_expr': 'icontains',
                },
            }
        }

    def filter_hpo_terms(self, queryset, name, value):
        return queryset.hpo_terms(hpo_terms=value)

    def filter_mode_of_inheritance_terms(self, queryset, name, value):
        return queryset.mode_of_inheritance_terms(hpo_terms=value)

    def filter_age_of_onset_terms(self, queryset, name, value):
        return queryset.age_of_onset_terms(hpo_terms=value)

    def filter_frequency_terms(self, queryset, name, value):
        return queryset.frequency_terms(hpo_terms=value)


class DiseaseGeneFilter(django_filters.rest_framework.FilterSet):

    symbol = django_filters.CharFilter(lookup_expr='iexact')
    status = DisplayChoiceFilter(choices=HGNC_GENE_STATUS)
    diseases = django_filters.ModelMultipleChoiceFilter(
        queryset=models.Disease.objects.fast(),
        widget=django_filters.widgets.CSVWidget,
        help_text='Multiple values may be separated by commas.',
    )
    hpo_terms = django_filters.BaseCSVFilter(
        label='HPO Terms',
        method='filter_hpo_terms',
        widget=django_filters.widgets.CSVWidget,
    )

    class Meta:
        model = Gene
        fields = [
            'symbol',
            'status',
            'active',
            'chromosome',
            'diseases',
        ]

    def filter_hpo_terms(self, queryset, name, value):
        return queryset.filter(
            Q(diseases__hpo_terms__identifier__in=[
                utils.normalize_hpo_id(x)
                for x in value
            ])
        )
