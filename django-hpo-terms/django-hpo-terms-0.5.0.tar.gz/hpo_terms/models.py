# -*- coding: utf-8 -*-
from django.core.validators import validate_comma_separated_integer_list
from django.db import models
from django.utils.translation import ugettext_lazy as _

from model_utils.models import TimeStampedModel

from . import choices, managers


class Term(models.Model):
    """HPO Terms.

    Source: http://purl.obolibrary.org/obo/hp.obo
    """

    version = models.ForeignKey('hpo_terms.Version', on_delete=models.CASCADE)
    identifier = models.PositiveIntegerField(db_index=True)
    label = models.CharField(max_length=255, blank=True)
    description = models.TextField(blank=True)
    created_by = models.CharField(max_length=50, blank=True)
    created = models.CharField(max_length=25, blank=True)
    modified = models.DateTimeField(auto_now=True)

    is_a = models.ManyToManyField('self', blank=True)
    can_be = models.ManyToManyField('self', blank=True)
    alternate_ids = models.CharField(
        max_length=500,
        blank=True,
        validators=[validate_comma_separated_integer_list]
    )

    objects = managers.TermQuerySet.as_manager()

    class Meta:
        verbose_name = _('Term')
        verbose_name_plural = _('Terms')
        index_together = [
            ['version', 'identifier']
        ]

    def __str__(self):
        return self.hpo_term

    @property
    def hpo_term(self):
        return 'HP:{0}'.format(str(self.identifier).zfill(7))

    @property
    def hpo_url(self):
        return 'http://compbio.charite.de/hpoweb/showterm?id={0}'.format(self.hpo_term)


class Version(TimeStampedModel):
    """Model to keep track of HPO version."""

    label = models.CharField(max_length=100)

    class Meta:
        verbose_name = _('Version')
        verbose_name_plural = _('Versions')

    def __str__(self):
        return self.label


class Synonym(TimeStampedModel):
    """Synonms for HPO terms."""

    hpo_term = models.ForeignKey(
        'hpo_terms.Term',
        related_name='synonyms',
        blank=True,
        null=True,
        on_delete=models.CASCADE,
    )
    description = models.TextField(blank=True)
    scope = models.PositiveSmallIntegerField(choices=choices.SYNONYM_SCOPES, blank=True, null=True)

    class Meta:
        verbose_name = _('Synonym')
        verbose_name_plural = _('Synonyms')

    def __str__(self):
        return str(self.hpo_term)


class CrossReference(TimeStampedModel):
    """XRefs for HPO terms."""

    hpo_term = models.ForeignKey(
        'hpo_terms.Term',
        related_name='xrefs',
        blank=True,
        null=True,
        on_delete=models.CASCADE,
    )
    source = models.PositiveSmallIntegerField(choices=choices.CROSS_REFERENCES)
    source_value = models.CharField(max_length=150)

    objects = managers.CrossReferenceQuerySet.as_manager()

    class Meta:
        verbose_name = _('XRef')
        verbose_name_plural = _('XRefs')

    def __str__(self):
        return str(self.hpo_term)


class Disease(TimeStampedModel):
    """A known disorder description. Stores OMIM and ORPHA terms.

    Note:
        Sources:
        - http://compbio.charite.de/jenkins/job/hpo.annotations/
        lastSuccessfulBuild/artifact/misc/phenotype_annotation.tab
        - http://compbio.charite.de/jenkins/job/hpo.annotations.monthly/
        lastSuccessfulBuild/artifact/annotation/genes_to_diseases.txt
    """

    version = models.ForeignKey('hpo_terms.Version', on_delete=models.CASCADE)
    database = models.PositiveSmallIntegerField(choices=choices.DATABASES)
    identifier = models.IntegerField()
    description = models.TextField(blank=True)
    qualifier = models.PositiveSmallIntegerField(choices=choices.QUALIFIERS, blank=True, null=True)
    evidence_code = models.PositiveSmallIntegerField(choices=choices.EVIDENCE, blank=True, null=True)
    mode_of_inheritance = models.ForeignKey(
        'hpo_terms.Term',
        on_delete=models.SET_NULL,
        related_name='disease_mois',
        blank=True,
        null=True,
    )
    age_of_onset = models.ForeignKey(
        'hpo_terms.Term',
        on_delete=models.SET_NULL,
        related_name='disease_age_of_onsets',
        blank=True,
        null=True,
    )
    frequency = models.ForeignKey(
        'hpo_terms.Term',
        on_delete=models.SET_NULL,
        related_name='disease_frequencies',
        blank=True,
        null=True,
    )
    create_date = models.DateField()
    assigned_by = models.CharField(max_length=255)
    hpo_terms = models.ManyToManyField(
        'hpo_terms.Term',
        related_name='diseases',
        blank=True,
    )
    genes = models.ManyToManyField(
        'genome.Gene',
        related_name='diseases',
        blank=True,
    )

    objects = managers.DiseaseQuerySet.as_manager()

    class Meta:
        verbose_name = _('Disease')
        verbose_name_plural = _('Diseases')
        unique_together = ('version', 'database', 'identifier')
        index_together = [
            ['database', 'identifier']
        ]

    def __str__(self):
        return self.label

    @property
    def label(self):
        return '{0}:{1}'.format(self.get_database_display(), self.identifier)

    @property
    def database_url(self):
        if self.get_database_display() == 'OMIM':
            return 'https://www.omim.org/entry/{0}'.format(str(self.identifier).zfill(6))
        elif self.get_database_display() == 'ORPHA':
            return 'http://www.orpha.net/consor/cgi-bin/OC_Exp.php?Lng=EN&Expert={0}'.format(str(self.identifier))
        elif self.get_database_display() == 'DECIPHER':
            return 'https://decipher.sanger.ac.uk/syndrome/{0}#overview'.format(str(self.identifier))

    @property
    def hpo_mode_of_inheritance_url(self):
        return self.mode_of_inheritance.hpo_url

    @property
    def hpo_age_of_onset_url(self):
        return self.age_of_onset.hpo_url

    @property
    def hpo_frequency_url(self):
        return self.frequency.hpo_url
