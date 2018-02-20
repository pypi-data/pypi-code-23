# copyright 2015-2016 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
# contact http://www.logilab.fr -- mailto:contact@logilab.fr
#
# This program is free software: you can redistribute it and/or modify it under
# the terms of the GNU Lesser General Public License as published by the Free
# Software Foundation, either version 2.1 of the License, or (at your option)
# any later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU Lesser General Public License for more
# details.
#
# You should have received a copy of the GNU Lesser General Public License along
# with this program. If not, see <http://www.gnu.org/licenses/>.
"""Simple Knowledge Organization System (SKOS) implementation for cubicweb
"""
import sys

from six import text_type, binary_type


def register_skos_concept_rdf_list_mapping(reg):
    """Register minimal SKOS mapping at the concept level (for use in
    'list.rdf' views).
    """
    reg.register_prefix('dc', 'http://purl.org/dc/elements/1.1/')
    reg.register_prefix('skos', 'http://www.w3.org/2004/02/skos/core#')
    reg.register_etype_equivalence('Concept', 'skos:Concept')
    reg.register_attribute_equivalence(
        'Concept', 'definition', 'skos:definition')
    reg.register_relation_equivalence(
        'Concept', 'in_scheme', 'ConceptScheme', 'skos:inScheme')


def register_skos_concept_rdf_output_mapping(reg, with_labels=True):
    """Register full SKOS mapping at the concept level (for use in
    'primary.rdf' views).
    """
    register_skos_concept_rdf_list_mapping(reg)
    reg.register_attribute_equivalence('Concept', 'example', 'skos:example')
    reg.register_relation_equivalence('Concept', 'broader_concept', 'Concept', 'skos:broader')
    reg.register_relation_equivalence('Concept', 'broader_concept', 'Concept', 'skos:narrower',
                                      reverse=True)
    reg.register_relation_equivalence('Concept', 'related_concept', 'Concept', 'skos:related')
    # may be a concept instead of an ExternalUri if the concept is locally known, but that is
    # handled by the importer
    reg.register_relation_equivalence('Concept', 'exact_match', 'ExternalUri', 'skos:exactMatch')
    reg.register_relation_equivalence('Concept', 'close_match', 'ExternalUri', 'skos:closeMatch')


def register_skos_rdf_list_mapping(reg):
    """Register minimal SKOS mapping, only describing concept scheme (for use in 'list.rdf' views).
    """
    reg.register_prefix('dc', 'http://purl.org/dc/elements/1.1/')
    reg.register_prefix('skos', 'http://www.w3.org/2004/02/skos/core#')
    reg.register_etype_equivalence('ConceptScheme', 'skos:ConceptScheme')
    reg.register_attribute_equivalence('ConceptScheme', 'title', 'dc:title')
    reg.register_attribute_equivalence('ConceptScheme', 'description', 'dc:description')


def register_skos_rdf_output_mapping(reg):
    """Register full SKOS mapping for outputing RDF from entities (for use in 'primary.rdf' views).

    Mapping doesn't include description for labels as it has to be handled manually, since yams
    models them as entities while SKOS uses literals.
    """
    register_skos_rdf_list_mapping(reg)
    register_skos_concept_rdf_output_mapping(reg, with_labels=False)


LABELS_RDF_MAPPING = {
    u'preferred_label': 'skos:prefLabel',
    u'alternative_label': 'skos:altLabel',
    u'hidden_label': 'skos:hiddenLabel',
}


def register_skos_rdf_input_mapping(reg):
    """Register SKOS mapping for input data.

    Mapping includes description for labels which should be included in `ExtEntity` for later
    transformation.
    """
    register_skos_rdf_list_mapping(reg)
    register_skos_rdf_output_mapping(reg)
    for rtype, predicate in LABELS_RDF_MAPPING.items():
        reg.register_relation_equivalence('Concept', rtype, 'Label', predicate)


def to_unicode(obj):
    """Turn some object (usually an exception) to unicode"""
    try:
        # The exception message might already be a unicode string.
        return text_type(obj)
    except UnicodeDecodeError:
        return binary_type(obj).decode(sys.getdefaultencoding(), 'ignore')
