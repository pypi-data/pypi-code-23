# -*- coding: utf-8
from django.contrib import admin

from . import models


class TermAdmin(admin.ModelAdmin):
    model = models.Term
    list_display = ('version', 'hpo_term', 'label', 'created_by', 'created', 'modified')
    raw_id_fields = ('version', 'is_a', 'can_be')
    search_fields = ('version__label', 'identifier', 'label', 'description', 'synonyms__description')
    save_as = True


class VersionAdmin(admin.ModelAdmin):
    model = models.Version
    list_display = ('label', 'created', 'modified')
    search_fields = ('label', )
    save_as = True


class SynonymAdmin(admin.ModelAdmin):
    model = models.Synonym
    list_display = ('hpo_term', 'scope', 'created', 'modified')
    list_filter = ('scope', )
    search_fields = ('description', )
    save_as = True


class CrossReferenceAdmin(admin.ModelAdmin):
    model = models.CrossReference
    list_display = ('hpo_term', 'source', 'source_value', 'created', 'modified')
    list_filter = ('source', )
    search_fields = ('source_value', )
    save_as = True


class DiseaseAdmin(admin.ModelAdmin):
    model = models.Disease
    list_display = (
        'label', 'qualifier', 'evidence_code',
        'mode_of_inheritance', 'age_of_onset', 'frequency',
        'create_date', 'created', 'modified'
    )
    raw_id_fields = ('mode_of_inheritance', 'age_of_onset', 'frequency', 'hpo_terms')
    list_filter = ('database', 'qualifier', 'evidence_code')
    search_fields = (
        'description',
        'hpo_terms__label',
        'hpo_terms__description',
        'hpo_terms__synonyms__description'
    )
    save_as = True


admin.site.register(models.Term, TermAdmin)
admin.site.register(models.Version, VersionAdmin)
admin.site.register(models.Synonym, SynonymAdmin)
admin.site.register(models.CrossReference, CrossReferenceAdmin)
admin.site.register(models.Disease, DiseaseAdmin)
