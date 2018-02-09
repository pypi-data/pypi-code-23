# -*- coding: utf-8 -*-
import datetime
import logging

from pronto import Ontology

from django.core.exceptions import ObjectDoesNotExist
from django.core.management import BaseCommand
from django.db.models import Q

from genome.models import Gene
from genomix.utils import retrieve_data

from hpo_terms import app_settings, choices, models, utils


logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Sync HPO from online resource'

    def handle(self, *args, **options):
        # Download external resources
        logger.info('Downloading HPO resources...')

        hpo = Ontology(app_settings.HPO_URL, timeout=10)
        hpo_diseases = retrieve_data(app_settings.HPO_DISEASES_URL)
        hpo_disease_genes = retrieve_data(app_settings.HPO_DISEASE_GENES_URL)

        logger.info('Checking HPO Version...')
        version = hpo.meta['data-version'][0]  # NOTE: pronto always returns array
        version_obj, version_created = models.Version.objects.get_or_create(label=version)

        if not version_created:
            logger.info('Version: {0} already synced!'.format(version))
        else:
            logger.info('Syncing new HPO terms with version: {0}'.format(version))

            relations = {}
            for term in hpo:
                identifier = utils.normalize_hpo_id(term.id)
                label = term.name
                description = term.desc
                created_by = term.other.get('created_by')
                created = term.other.get('creation_date')

                alternate_ids = [
                    str(utils.normalize_hpo_id(alt_term))
                    for alt_term in term.other.get('alt_id', [])
                ]

                try:
                    term_obj = models.Term.objects.create(
                        version=version_obj,
                        identifier=identifier,
                        label=label if label else "",
                        description=description if description else "",
                        created_by=created_by[0] if created_by else "",
                        created=created[0] if created else "",
                        alternate_ids=",".join(alternate_ids),
                    )
                except Exception as error:
                    msg = 'HPO: {0} could not be added! Error: {1}'.format(term.id, error)
                    logger.error(msg)
                    raise Exception(msg)

                # Create Synonym objects
                for synonym in term.synonyms:
                    if synonym:
                        synonym_obj, synonym_created = models.Synonym.objects.get_or_create(
                            hpo_term=term_obj,
                            description=synonym.desc if synonym.desc else "",
                            # NOTE: pronto always returns array
                            scope=getattr(choices.SYNONYM_SCOPES, synonym.scope),
                        )

                # Save is_a/can_be relations to add the ManyToManyFields once completed
                relations[term_obj.id] = {'is_a': [], 'can_be': []}
                for key, value in term.relations.items():
                    if str(key) == "Relationship('is_a')":
                        for is_a_term in value:
                            relations[term_obj.id]['is_a'].append(utils.normalize_hpo_id(is_a_term.id))
                    elif str(key) == "Relationship('can_be')":
                        for can_be_term in value:
                            relations[term_obj.id]['can_be'].append(utils.normalize_hpo_id(can_be_term.id))
                    else:
                        err = "Parsing {0} is not implemented!".format(str(key))
                        raise NotImplementedError(err)

                # Create CrossReference objects
                for xref in term.other.get('xref', []):
                    if xref:
                        xref_data = xref.split(':', 1)

                        # NOTE: We want source and id to store. There are 3 records that don't conform
                        if len(xref_data) != 2 or xref_data[0].upper() == 'HTTP':
                            err_msg = 'Format of XRef: {0} for {1} is not supported!'.format(xref, term.id)
                            logger.warning(err_msg)
                            continue

                        xref_obj, xref_created = models.CrossReference.objects.get_or_create(
                            hpo_term=term_obj,
                            # NOTE: pronto always returns array
                            source=getattr(choices.CROSS_REFERENCES, str(xref_data[0].upper())),
                            source_value=xref_data[1],
                        )

            # Create is_a/can_be relationships
            logger.info('Building is_a/can_be relationships...')
            for key, value in relations.items():
                term_obj = models.Term.objects.get(pk=key)

                is_a_objects = models.Term.objects.filter(
                    Q(version=version_obj) &
                    Q(identifier__in=value['is_a'])
                )
                term_obj.is_a.add(*is_a_objects)

                can_be_objects = models.Term.objects.filter(
                    Q(version=version_obj) &
                    Q(identifier__in=value['can_be'])
                )
                term_obj.can_be.add(*can_be_objects)

                term_obj.save()

                if len(is_a_objects) != len(value['is_a']):
                    msg = 'Syncing is_a for Term: {0} failed! {1} vs {2}'.format(
                        key, is_a_objects, value
                    )
                    logger.error(msg)
                    raise ValueError(msg)

                if len(can_be_objects) != len(value['can_be']):
                    msg = 'Syncing can_be for Term: {0} failed! {1} vs {2}'.format(
                        key, can_be_objects, value
                    )
                    logger.error(msg)
                    raise ValueError(msg)

            # Create Disease objects
            logger.info('Syncing diseases from HPO...')
            for line in hpo_diseases:
                disease_record = line.strip().split('\t')

                # NOTE: some OMIM records are screwed up, we skip those
                try:
                    identifier = int(disease_record[1])
                except ValueError:
                    logger.warning('Skipping: {0}'.format(disease_record))
                    continue

                database = getattr(choices.DATABASES, disease_record[0])

                description = disease_record[2]
                qualifier = getattr(choices.QUALIFIERS, disease_record[3], None)
                evidence_code = getattr(choices.EVIDENCE, disease_record[6], None)
                age_of_onset = disease_record[7].strip()
                frequency = disease_record[8].strip()
                create_date = disease_record[12]
                assigned_by = disease_record[13]

                if age_of_onset:
                    try:
                        age_of_onset_obj = models.Term.objects.get(
                            identifier=utils.normalize_hpo_id(age_of_onset)
                        )
                    except ObjectDoesNotExist:
                        age_of_onset_obj = None
                else:
                    age_of_onset_obj = None

                if frequency:
                    try:
                        frequency_obj = models.Term.objects.get(
                            identifier=utils.normalize_hpo_id(frequency)
                        )
                    except ObjectDoesNotExist:
                        frequency_obj = None
                else:
                    frequency_obj = None

                disease_obj, updated = models.Disease.objects.update_or_create(
                    version=version_obj,
                    database=database,
                    identifier=identifier,
                    defaults={
                        'description': description,
                        'qualifier': qualifier,
                        'evidence_code': evidence_code,
                        'age_of_onset': age_of_onset_obj,
                        'frequency': frequency_obj,
                        'create_date': create_date,
                        'assigned_by': assigned_by,
                    }
                )

                hpo_term = models.Term.objects.get(
                    identifier=utils.normalize_hpo_id(disease_record[4])
                )

                disease_obj.hpo_terms.add(hpo_term)
                disease_obj.save()

            # Create Disease Gene objects
            logger.info('Syncing disease genes from HPO')
            for line in hpo_disease_genes:
                if line.startswith('#'):  # NOTE: Skips header
                    continue

                (gene_id, symbol, disease) = line.split('\t')
                (database, identifier) = disease.strip().split(':')

                try:
                    gene_obj = Gene.objects.get(symbol__iexact=symbol)
                except ObjectDoesNotExist:
                    msg = 'Gene: {0} not in the database!'.format(symbol)
                    logger.warning(msg)

                disease_obj, created = models.Disease.objects.get_or_create(
                    version=version_obj,
                    database=getattr(choices.DATABASES, database),
                    identifier=int(identifier),
                    defaults={
                        'create_date': datetime.datetime.now().date()
                    }
                )

                disease_obj.genes.add(gene_obj)
                disease_obj.save()
