# -*- coding: utf-8 -*-
from django.db.models import Q, QuerySet
from . import utils


class TermQuerySet(QuerySet):

    def fast(self):
        return self.select_related('version').prefetch_related('is_a').all()

    def hpo_term(self, hpo_term):
        """Filters for a HPO term.

        Arguments:
            hpo_term (str): HPO Term.

        Returns:
            QuerySet: CrossReference objects
        """
        return self.fast().filter(
            Q(identifier=utils.normalize_hpo_id(hpo_term)),
        )

    def is_a_terms(self, hpo_terms):
        """Filters for a list of is a HPO terms.

        Arguments:
            hpo_terms (list): List of HPO terms.

        Returns:
            QuerySet: Term objects
        """
        return self.fast().filter(
            Q(is_a__identifier__in=[utils.normalize_hpo_id(x) for x in hpo_terms]),
        )

    def can_be_terms(self, hpo_terms):
        """Filters for a list of can be HPO terms.

        Arguments:
            hpo_terms (list): List of HPO terms.

        Returns:
            QuerySet: Term objects
        """
        return self.fast().filter(
            Q(can_be__identifier__in=[utils.normalize_hpo_id(x) for x in hpo_terms]),
        )


class CrossReferenceQuerySet(QuerySet):

    def fast(self):
        return self.select_related('hpo_term').all()

    def hpo_terms(self, hpo_terms):
        """Filters for a list of HPO terms.

        Arguments:
            hpo_terms (list): List of HPO terms.

        Returns:
            QuerySet: CrossReference objects
        """
        return self.fast().filter(
            Q(hpo_term__identifier__in=[utils.normalize_hpo_id(x) for x in hpo_terms]),
        )


class DiseaseQuerySet(QuerySet):

    def fast(self):
        return self.select_related('version') \
            .select_related('age_of_onset__version') \
            .prefetch_related('hpo_terms__version') \
            .prefetch_related('genes') \
            .all()

    def hpo_terms(self, hpo_terms):
        """Filters for a list of HPO terms.

        Arguments:
            hpo_terms (list): List of HPO terms.

        Returns:
            QuerySet: CrossReference objects
        """
        return self.fast().filter(
            Q(hpo_terms__identifier__in=[utils.normalize_hpo_id(x) for x in hpo_terms]),
        )

    def mode_of_inheritance_terms(self, hpo_terms):
        """Filters for a Mode of Inheritance (using HPO Terms).

        Arguments:
            hpo_terms (list): HPO terms.

        Returns:
            QuerySet: Disease objects
        """
        return self.fast().filter(
            Q(mode_of_inheritance__identifier__in=[utils.normalize_hpo_id(x) for x in hpo_terms]),
        )

    def age_of_onset_terms(self, hpo_terms):
        """Filters for a Age of Onset (using HPO Terms).

        Arguments:
            hpo_terms (list): HPO terms.

        Returns:
            QuerySet: Disease objects
        """
        return self.fast().filter(
            Q(age_of_onset__identifier__in=[utils.normalize_hpo_id(x) for x in hpo_terms]),
        )

    def frequency_terms(self, hpo_terms):
        """Filters for a Frequency (using HPO Terms).

        Arguments:
            hpo_terms (list): HPO terms.

        Returns:
            QuerySet: Disease objects
        """
        return self.fast().filter(
            Q(frequency__identifier__in=[utils.normalize_hpo_id(x) for x in hpo_terms]),
        )
