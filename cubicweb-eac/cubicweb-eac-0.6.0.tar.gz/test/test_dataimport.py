# coding: utf-8
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
"""cubicweb-eac unit tests for dataimport"""

import datetime
from io import BytesIO
from itertools import count
from os.path import join, dirname
import sys
import unittest

from six import reraise
from six.moves import map

from cubicweb import NoResultError
from cubicweb.dataimport.importer import ExtEntity, SimpleImportLog
from cubicweb.devtools.testlib import CubicWebTC

from cubicweb_eac import dataimport, testutils


def mock_(string):
    return string


def tolist(dic):
    """Transform sets in `dic` values as lists for easier comparison."""
    for k, v in dic.items():
        if isinstance(v, set):
            v = list(v)
        dic[k] = v
    return dic


def extentities2dict(entities):
    edict = {}
    for extentity in entities:
        edict.setdefault(extentity.etype, {})[extentity.extid] = extentity.values
    return edict


class EACXMLParserTC(unittest.TestCase):

    if sys.version_info < (3, 2):
        assertCountEqual = unittest.TestCase.assertItemsEqual

    @classmethod
    def datapath(cls, *fname):
        """joins the object's datadir and `fname`"""
        return join(dirname(__file__), 'data', *fname)

    def file_extentities(self, fname):
        fpath = self.datapath(fname)
        import_log = SimpleImportLog(fpath)
        # Use a predictable extid_generator.
        extid_generator = map(str, count()).next
        importer = dataimport.EACCPFImporter(fpath, import_log, mock_,
                                             extid_generator=extid_generator)
        return importer.external_entities()

    def test_parse_FRAD033_EAC_00001(self):
        _gen_extid = map(str, (x for x in count() if x != 2)).next
        expected = [
            ('AuthorityRecord', 'FRAD033_EAC_00001',
             {'isni': set([u'22330001300016']),
              'start_date': set([datetime.date(1800, 1, 1)]),
              'end_date': set([datetime.date(2099, 1, 1)]),
              'agent_kind': set(['agentkind/authority']),
              'record_id': set(['FRAD033_EAC_00001']),
             },
            ),
            ('EACOtherRecordId', _gen_extid(),
             {'eac_other_record_id_of': set(['FRAD033_EAC_00001']),
              'value': set([u'1234']),
             },
            ),
            ('EACOtherRecordId', _gen_extid(),
             {'eac_other_record_id_of': set(['FRAD033_EAC_00001']),
              'value': set([u'ABCD']),
              'local_type': set([u'letters']),
             },
            ),
            ('EACSource', _gen_extid(),
             {'source_agent': set(['FRAD033_EAC_00001']),
              'title': set([u'1. Ouvrages imprimés...']),
              'description': set([u'des bouquins']),
              'description_format': set([u'text/plain']),
              },
             ),
            ('EACSource', _gen_extid(),
             {'source_agent': set(['FRAD033_EAC_00001']),
              'url': set([u'http://archives.gironde.fr']),
              'title': set([u'Site des Archives départementales de la Gironde']),
             },
            ),
            ('Activity', _gen_extid(),
             {'type': set([u'create']),
              'generated': set(['FRAD033_EAC_00001']),
              'start': set([datetime.datetime(2013, 4, 24, 5, 34, 41)]),
              'end': set([datetime.datetime(2013, 4, 24, 5, 34, 41)]),
              'description': set([u'bla bla']),
              'description_format': set([u'text/plain']),
             },
            ),
            ('Activity', _gen_extid(),
             {'generated': set(['FRAD033_EAC_00001']),
              'type': set([u'modify']),
              'start': set([datetime.datetime(2015, 1, 15, 7, 16, 33)]),
              'end': set([datetime.datetime(2015, 1, 15, 7, 16, 33)]),
              'agent': set([u'Delphine Jamet'])
             },
            ),
            ('AgentKind', 'agentkind/authority',
             {'name': set([u'authority'])},
            ),
            ('NameEntry', _gen_extid(),
             {'parts': set([u'Gironde, Conseil général']),
              'form_variant': set([u'authorized']),
              'name_entry_for': set(['FRAD033_EAC_00001']),
             },
            ),
            ('NameEntry', _gen_extid(),
             {'parts': set([u'CG33']),
              'form_variant': set([u'alternative']),
              'name_entry_for': set(['FRAD033_EAC_00001']),
             },
            ),
            ('PostalAddress', _gen_extid(),
             {'street': set([u'1 Esplanade Charles de Gaulle']),
              'postalcode': set([u'33074']),
              'city': set([u' Bordeaux Cedex']),
             },
            ),
            ('AgentPlace', _gen_extid(),
             {'name': set([u'Bordeaux (Gironde, France)']),
              'role': set([u'siege']),
              'place_agent': set(['FRAD033_EAC_00001']),
              'place_address': set(['9']),
              'equivalent_concept': set([u'http://catalogue.bnf.fr/ark:/12148/cb152418385']),
             },
            ),
            ('AgentPlace', _gen_extid(),
             {'name': set([u'Toulouse (France)']),
              'place_agent': set(['FRAD033_EAC_00001']),
              'role': set([u'domicile']),
             },
            ),
            ('AgentPlace', _gen_extid(),
             {'name': set([u'Lit']),
              'place_agent': set(['FRAD033_EAC_00001']),
              'role': set([u'dodo']),
             },
            ),
            ('LegalStatus', _gen_extid(),
             {'term': set([u'Collectivité territoriale']),
              'start_date': set([datetime.date(1234, 1, 1)]),
              'end_date': set([datetime.date(3000, 1, 1)]),
              'description': set([u'Description du statut']),
              'description_format': set([u'text/plain']),
              'legal_status_agent': set(['FRAD033_EAC_00001']),
             },
            ),
            ('Mandate', _gen_extid(),
             {'term': set([u'1. Constitutions françaises']),
              'description': set([u'Description du mandat']),
              'description_format': set([u'text/plain']),
              'mandate_agent': set(['FRAD033_EAC_00001']),
             },
            ),
            ('History', _gen_extid(),
             {'text': set(["\n".join((
                     u'<p xmlns="urn:isbn:1-931666-33-4" '
                     u'xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" '
                     u'xmlns:xlink="http://www.w3.org/1999/xlink">{0}</p>'
                  ).format(text) for text in [u"La loi du 22 décembre 1789, en divisant ...",
                                              u"L'inspecteur Canardo"])
              ]),
              'text_format': set([u'text/html']),
              'history_agent': set(['FRAD033_EAC_00001']),
              'has_citation': set(['16', '17']),
             },
            ),
            ('Citation', _gen_extid(),
             {'uri': set(['http://www.assemblee-nationale.fr/histoire/images-decentralisation/decentralisation/loi-du-22-decembre-1789-.pdf'])},  # noqa
            ),
            ('Citation', _gen_extid(),
             {'uri': set(['http://pifgadget']), 'note': set(['Voir aussi pifgadget'])},
            ),
            ('Structure', _gen_extid(),
             {'description': set([u'<p xmlns="urn:isbn:1-931666-33-4" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xlink="http://www.w3.org/1999/xlink">Pour accomplir ses missions ...</p>']),  # noqa
              'description_format': set([u'text/html']),
              'structure_agent': set(['FRAD033_EAC_00001']),
             },
            ),
            ('AgentFunction', _gen_extid(),
             {'description': set([u'<p xmlns="urn:isbn:1-931666-33-4" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xlink="http://www.w3.org/1999/xlink">Quatre grands domaines de compétence...</p>']),  # noqa
              'description_format': set([u'text/html']),
              'function_agent': set(['FRAD033_EAC_00001']),
             },
            ),
            ('AgentFunction', _gen_extid(),
             {'name': set([u'action sociale']),
              'function_agent': set(['FRAD033_EAC_00001']),
              'description': set([u'<p xmlns="urn:isbn:1-931666-33-4" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xlink="http://www.w3.org/1999/xlink">1. Solidarité\n'  # noqa
                                  u'            blablabla.</p>']),
              'description_format': set([u'text/html']),
              'equivalent_concept': set([
                  u'http://data.culture.fr/thesaurus/page/ark:/67717/T1-200'
              ]),
             },
            ),
            ('AgentFunction', _gen_extid(),
             {'name': set([u'environnement']),
              'function_agent': set(['FRAD033_EAC_00001']),
              'equivalent_concept': set([
                  u'http://data.culture.fr/thesaurus/page/ark:/67717/T1-1074']),
             },
            ),
            ('Occupation', _gen_extid(),
             {'term': set([u'Réunioniste']),
              'start_date': set([datetime.date(1987, 1, 1)]),
              'end_date': set([datetime.date(2099, 1, 1)]),
              'description': set([u'Organisation des réunions ...']),
              'description_format': set([u'text/plain']),
              'occupation_agent': set(['FRAD033_EAC_00001']),
              'has_citation': set(['23']),
              'equivalent_concept': set(['http://pifgadget.com']),
             },
            ),
            ('Citation', _gen_extid(),
             {'note': set([u'la bible']),
             },
            ),
            ('GeneralContext', _gen_extid(),
             {'content': set([u'<p xmlns="urn:isbn:1-931666-33-4" '
                              u'xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" '
                              u'xmlns:xlink="http://www.w3.org/1999/xlink">very famous</p>']),
              'content_format': set([u'text/html']),
              'has_citation': set(['25']),
              'general_context_of': set(['FRAD033_EAC_00001']),
              }
            ),
            ('Citation', _gen_extid(),
             {'note': set([u'it\'s well known']),
             },
            ),
            ('ExternalUri', 'CG33-DIRADSJ',
             {'uri': set([u'CG33-DIRADSJ']),
              'cwuri': set([u'CG33-DIRADSJ']),
             },
            ),
            ('HierarchicalRelation', _gen_extid(),
             {'start_date': set([datetime.date(2008, 1, 1)]),
              'end_date': set([datetime.date(2099, 1, 1)]),
              'entry': set([u"Gironde. Conseil général. Direction de l'administration et de "
                            u"la sécurité juridique"]),
              'description': set([u'Coucou']),
              'description_format': set([u'text/plain']),
              'hierarchical_parent': set(['CG33-DIRADSJ']),
              'hierarchical_child': set(['FRAD033_EAC_00001']),
             },
            ),
            ('ExternalUri', 'whatever',
             {'uri': set([u'whatever']),
              'cwuri': set([u'whatever']),
             },
            ),
            ('ExternalUri', '/dev/null',
             {'uri': set([u'/dev/null']),
              'cwuri': set([u'/dev/null']),
             },
            ),
            ('ChronologicalRelation', _gen_extid(),
             {'chronological_predecessor': set(['whatever']),
              'chronological_successor': set(['FRAD033_EAC_00001']),
              'start_date': set([datetime.date(1917, 1, 1)]),
              'end_date': set([datetime.date(2009, 1, 1)]),
              'entry': set([u'CG32']),
             },
            ),
            ('ChronologicalRelation', _gen_extid(),
             {'chronological_predecessor': set(['FRAD033_EAC_00001']),
              'chronological_successor': set(['/dev/null']),
              'start_date': set([datetime.date(2042, 1, 1)]),
              'xml_wrap': set(['<gloups xmlns="urn:isbn:1-931666-33-4" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xlink="http://www.w3.org/1999/xlink">hips</gloups>']),  # noqa
              'entry': set([u'Trash']),
             },
            ),
            ('AssociationRelation', _gen_extid(),
             {'association_from': set(['FRAD033_EAC_00001']),
              'association_to': set(['agent-x']),
             },
            ),
            ('EACResourceRelation', _gen_extid(),
             {'agent_role': set([u'creatorOf']),
              'resource_role': set([u'Fonds d\'archives']),
              'resource_relation_resource': set([
                  'http://gael.gironde.fr/ead.html?id=FRAD033_IR_N']),
              'resource_relation_agent': set(['FRAD033_EAC_00001']),
              'start_date': set([datetime.date(1673, 1, 1)]),
              'end_date': set([datetime.date(1963, 1, 1)]),
              'xml_wrap': set(['<he xmlns="urn:isbn:1-931666-33-4" xmlns:xlink="http://www.w3.org/1999/xlink" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">joe</he>']),  # noqa
             },
            ),
            ('ExternalUri', 'http://gael.gironde.fr/ead.html?id=FRAD033_IR_N',
             {'uri': set([u'http://gael.gironde.fr/ead.html?id=FRAD033_IR_N']),
              'cwuri': set([u'http://gael.gironde.fr/ead.html?id=FRAD033_IR_N'])},
            ),
            ('ExternalUri', 'agent-x',
             {'uri': set([u'agent-x']), 'cwuri': set([u'agent-x'])},
            ),
            ('ExternalUri', 'http://data.culture.fr/thesaurus/page/ark:/67717/T1-200',
             {'uri': set([u'http://data.culture.fr/thesaurus/page/ark:/67717/T1-200']),
              'cwuri': set([u'http://data.culture.fr/thesaurus/page/ark:/67717/T1-200'])},
            ),
            ('ExternalUri', 'http://data.culture.fr/thesaurus/page/ark:/67717/T1-1074',
             {'uri': set([u'http://data.culture.fr/thesaurus/page/ark:/67717/T1-1074']),
              'cwuri': set([u'http://data.culture.fr/thesaurus/page/ark:/67717/T1-1074'])},
            ),
            ('ExternalUri', 'http://catalogue.bnf.fr/ark:/12148/cb152418385',
             {'uri': set([u'http://catalogue.bnf.fr/ark:/12148/cb152418385']),
              'cwuri': set([u'http://catalogue.bnf.fr/ark:/12148/cb152418385'])},
            ),
            ('ExternalUri', 'http://pifgadget.com',
             {'uri': set([u'http://pifgadget.com']),
              'cwuri': set([u'http://pifgadget.com'])},
            ),
        ]
        expected = [ExtEntity(*vals) for vals in expected]
        fpath = self.datapath('FRAD033_EAC_00001_simplified.xml')
        import_log = SimpleImportLog(fpath)
        # Use a predictable extid_generator.
        extid_generator = map(str, count()).next
        importer = dataimport.EACCPFImporter(fpath, import_log, mock_,
                                             extid_generator=extid_generator)
        entities = list(importer.external_entities())
        self.check_external_entities(entities, expected)
        visited = set([])
        for x in importer._visited.values():
            visited.update(x)
        self.assertItemsEqual(visited, [x.extid for x in expected])
        # Gather not-visited tag by name and group source lines.
        not_visited = {}
        for tagname, sourceline in importer.not_visited():
            not_visited.setdefault(tagname, set([])).add(sourceline)
        self.assertEqual(not_visited,
                         {'maintenanceStatus': set([12]),
                          'publicationStatus': set([14]),
                          'maintenanceAgency': set([16]),
                          'languageDeclaration': set([21]),
                          'conventionDeclaration': set([25, 35, 44]),
                          'localControl': set([54]),
                          'source': set([76]),  # empty.
                          'structureOrGenealogy': set([189]),  # empty.
                          'biogHist': set([204]),  # empty.
                          })

    def test_mandate_under_mandates(self):
        """In FRAD033_EAC_00003.xml, <mandate> element are within <mandates>."""
        entities = list(self.file_extentities('FRAD033_EAC_00003.xml'))
        expected_terms = [
            u'Code du patrimoine, Livre II',
            u'Loi du 5 brumaire an V [26 octobre 1796]',
            (u'Loi du 3 janvier 1979 sur les archives, accompagnée de ses décrets\n'
             u'                        d’application datant du 3 décembre.'),
            u'Loi sur les archives du 15 juillet 2008',
        ]
        self.assertCountEqual([next(iter(x.values['term'])) for x in entities
                               if x.etype == 'Mandate' and 'term' in x.values],
                              expected_terms)
        mandate_with_link = next(x for x in entities if x.etype == 'Mandate' and
                                 u'Code du patrimoine, Livre II' in x.values['term'])
        extid = next(iter(mandate_with_link.values['has_citation']))
        url = u'http://www.legifrance.gouv.fr/affichCode.do?idArticle=LEGIARTI000019202816'
        citation = next(x for x in entities if x.etype == 'Citation'
                        and url in x.values['uri'])
        self.assertEqual(extid, citation.extid)

    def test_agentfunction_within_functions_tag(self):
        """In FRAD033_EAC_00003.xml, <function> element are within <functions>
        not <description>.
        """
        entities = self.file_extentities('FRAD033_EAC_00003.xml')
        self.assertCountEqual(
            [x.values['name'].pop() for x in entities
             if x.etype == 'AgentFunction' and 'name' in x.values],
            [u'contr\xf4le', u'collecte', u'classement', u'restauration', u'promotion'])

    def test_no_nameentry_authorizedform(self):
        entities = self.file_extentities(
            "Service de l'administration generale et des assemblees.xml")
        expected = (u"Gironde. Conseil général. Service de l'administration "
                    u"générale et des assemblées")
        self.assertIn(expected, [x.values['parts'].pop() for x in entities
                                 if x.etype == 'NameEntry'])

    def ctx_assert(self, method, actual, expected, ctx, msg=None):
        """Wrap assertion method with a context message"""
        try:
            getattr(self, method)(actual, expected, msg=msg)
        except AssertionError as exc:
            msg = str(exc)
            if ctx:
                msg = ('[%s] ' % ctx) + msg
            reraise(AssertionError, AssertionError(msg), sys.exc_info()[-1])

    def check_external_entities(self, entities, expected):
        entities = extentities2dict(entities)
        expected = extentities2dict(expected)
        etypes, expected_etypes = list(entities), list(expected)
        self.ctx_assert('assertCountEqual', etypes, expected_etypes, ctx='etypes')

        def safe_int(value):
            try:
                return int(value)
            except ValueError:
                return 9999

        ordered_etypes = [x[1] for x in sorted((min(safe_int(extid) for extid in edict), etype)
                                               for etype, edict in expected.items())]
        for etype in ordered_etypes:
            edict = expected[etype]
            entities_etype = entities[etype]
            extids, expected_extids = list(entities_etype), list(edict)
            self.ctx_assert('assertCountEqual', extids, expected_extids,
                            ctx='%s/extids' % etype)
            for extid, values in edict.items():
                self.ctx_assert('assertEqual',
                                tolist(entities_etype[extid]), tolist(values),
                                ctx='%s/%s/values' % (etype, extid))

    def test_errors(self):
        log = SimpleImportLog('<dummy>')
        with self.assertRaises(dataimport.InvalidXML):
            importer = dataimport.EACCPFImporter(BytesIO('no xml'), log, mock_)
            list(importer.external_entities())
        with self.assertRaises(dataimport.MissingTag):
            importer = dataimport.EACCPFImporter(BytesIO('<xml/>'), log, mock_)
            list(importer.external_entities())


class EACDataImportTC(CubicWebTC):

    def test_FRAD033_EAC_00001(self):
        fpath = self.datapath('FRAD033_EAC_00001_simplified.xml')
        with self.admin_access.repo_cnx() as cnx:
            # create a skos concept to ensure it's used instead of a ExternalUri
            scheme = cnx.create_entity('ConceptScheme')
            scheme.add_concept(u'environnement',
                               cwuri=u'http://data.culture.fr/thesaurus/page/ark:/67717/T1-1074')
            cnx.commit()
            created, updated = testutils.eac_import(cnx, fpath)
            self.assertEqual(len(created), 39)
            self.assertEqual(updated, set())
            rset = cnx.find('AuthorityRecord', isni=u'22330001300016')
            self.assertEqual(len(rset), 1)
            record = rset.one()
            self.assertEqual(record.kind, 'authority')
            self.assertEqual(record.start_date, datetime.date(1800, 1, 1))
            self.assertEqual(record.end_date, datetime.date(2099, 1, 1))
            self.assertEqual(record.other_record_ids,
                             [(None, '1234'), ('letters', 'ABCD')])
            address = record.postal_address[0]
            self.assertEqual(address.street, u'1 Esplanade Charles de Gaulle')
            self.assertEqual(address.postalcode, u'33074')
            self.assertEqual(address.city, u' Bordeaux Cedex')
            rset = cnx.execute('Any R,N WHERE P place_agent A, A eid %(eid)s, P role R, P name N',
                               {'eid': record.eid})
            self.assertCountEqual(rset.rows,
                                  [[u'siege', u'Bordeaux (Gironde, France)'],
                                   [u'domicile', u'Toulouse (France)'],
                                   [u'dodo', u'Lit']])
            self.assertEqual(len(record.reverse_function_agent), 3)
            for related in ('structure', 'history', 'mandate', 'occupation',
                            'generalcontext', 'legal_status', 'eac_relations',
                            'equivalent_concept', 'control'):
                with self.subTest(related=related):
                    checker = getattr(self, '_check_' + related)
                    checker(cnx, record)

    def _check_structure(self, cnx, record):
        rset = cnx.find('Structure', structure_agent=record)
        self.assertEqual(len(rset), 1)
        self.assertEqual(rset.one().printable_value('description',
                                                    format=u'text/plain').strip(),
                         u'Pour accomplir ses missions ...')

    def _check_history(self, cnx, record):
        rset = cnx.find('History', history_agent=record)
        self.assertEqual(len(rset), 1)
        self.assertEqual(rset.one().printable_value('text',
                                                    format=u'text/plain').strip(),
                         u"La loi du 22 décembre 1789, en divisant ...\n\nL'inspecteur Canardo")

    def _check_mandate(self, cnx, record):
        rset = cnx.find('Mandate', mandate_agent=record)
        self.assertEqual(len(rset), 1)
        self.assertEqual(rset.one().printable_value('description',
                                                    format=u'text/plain').strip(),
                         u'Description du mandat')

    def _check_occupation(self, cnx, record):
        occupation = cnx.find('Occupation', occupation_agent=record).one()
        self.assertEqual(occupation.term, u'Réunioniste')
        citation = occupation.has_citation[0]
        self.assertEqual(citation.note, u'la bible')
        voc = occupation.equivalent_concept[0]
        self.assertEqual(voc.uri, u'http://pifgadget.com')

    def _check_generalcontext(self, cnx, record):
        occupation = cnx.find('GeneralContext', general_context_of=record).one()
        self.assertIn(u'very famous', occupation.content)
        self.assertEqual(occupation.content_format, u'text/html')
        citation = occupation.has_citation[0]
        self.assertEqual(citation.note, u'it\'s well known')

    def _check_legal_status(self, cnx, record):
        rset = cnx.find('LegalStatus', legal_status_agent=record)
        self.assertEqual(len(rset), 1)
        self.assertEqual(rset.one().printable_value('description',
                                                    format=u'text/plain').strip(),
                         u'Description du statut')

    def _check_eac_relations(self, cnx, record):
        relation = cnx.find('HierarchicalRelation').one()
        self.assertEqual(relation.entry,
                         u"Gironde. Conseil général. Direction de "
                         u"l'administration et de la sécurité juridique")
        self.assertEqual(relation.printable_value('description',
                                                  format='text/plain'),
                         u"Coucou")
        other_record = cnx.find('ExternalUri', uri=u'CG33-DIRADSJ').one()
        self.assertEqual(relation.hierarchical_parent[0], other_record)
        relation = cnx.find('AssociationRelation').one()
        self.assertEqual(relation.association_from[0], record)
        other_record = cnx.find('ExternalUri', uri=u'agent-x').one()
        self.assertEqual(other_record.cwuri, 'agent-x')
        self.assertEqual(relation.association_to[0], other_record)
        rset = cnx.find('EACResourceRelation', agent_role=u'creatorOf')
        self.assertEqual(len(rset), 1)
        rrelation = rset.one()
        self.assertEqual(rrelation.resource_relation_agent[0], record)
        exturi = rrelation.resource_relation_resource[0]
        self.assertEqual(exturi.uri,
                         u'http://gael.gironde.fr/ead.html?id=FRAD033_IR_N')
        self.assertEqual(rrelation.xml_wrap.getvalue(),
                         '<he xmlns="urn:isbn:1-931666-33-4" xmlns:xlink="http://www.w3.org/1999/xlink" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">joe</he>')  # noqa

    def _check_equivalent_concept(self, cnx, record):
        functions = dict((f.name, f) for f in record.reverse_function_agent)
        self.assertEqual(functions['action sociale'].equivalent_concept[0].cwuri,
                         'http://data.culture.fr/thesaurus/page/ark:/67717/T1-200')
        self.assertEqual(functions['action sociale'].equivalent_concept[0].cw_etype,
                         'ExternalUri')
        self.assertEqual(functions['environnement'].equivalent_concept[0].cwuri,
                         'http://data.culture.fr/thesaurus/page/ark:/67717/T1-1074')
        self.assertEqual(functions['environnement'].equivalent_concept[0].cw_etype,
                         'Concept')
        self.assertEqual(functions['environnement'].vocabulary_source[0].eid,
                         functions['environnement'].equivalent_concept[0].scheme.eid)
        place = cnx.find('AgentPlace', role=u'siege').one()
        self.assertEqual(place.equivalent_concept[0].cwuri,
                         'http://catalogue.bnf.fr/ark:/12148/cb152418385')

    def _check_control(self, cnx, record):
        rset = cnx.find('EACSource')
        self.assertEqual(len(rset), 2)
        rset = cnx.execute('Any A WHERE A generated X, X eid %(x)s', {'x': record.eid})
        self.assertEqual(len(rset), 2)
        rset = cnx.execute('Any A WHERE A agent "Delphine Jamet"')
        self.assertEqual(len(rset), 1)

    def test_multiple_imports(self):
        def count_entity(cnx, etype):
            return cnx.execute('Any COUNT(X) WHERE X is %s' % etype)[0][0]

        with self.admin_access.repo_cnx() as cnx:
            nb_records_before = count_entity(cnx, 'AuthorityRecord')
            for fname in ('FRAD033_EAC_00001.xml', 'FRAD033_EAC_00003.xml',
                          'FRAD033_EAC_00071.xml'):
                fpath = self.datapath(fname)
                created, updated = testutils.eac_import(cnx, fpath)
            nb_records_after = count_entity(cnx, 'AuthorityRecord')
            self.assertEqual(nb_records_after - nb_records_before, 3)

    def test_unknown_kind(self):
        with self.admin_access.repo_cnx() as cnx:
            testutils.eac_import(cnx, self.datapath('custom_kind.xml'))
            self.assertRaises(NoResultError, cnx.find('AgentKind', name=u'a custom kind').one)
            self.assertEqual(cnx.find('AuthorityRecord').one().agent_kind[0].name,
                             'unknown-agent-kind')

    def test_no_name_entry(self):
        with self.admin_access.repo_cnx() as cnx:
            with self.assertRaises(dataimport.MissingTag) as cm:
                testutils.eac_import(cnx, self.datapath('no_name_entry.xml'))
            self.assertEqual(cm.exception.tag, 'nameEntry')
            self.assertEqual(cm.exception.tag_parent, 'identity')

    def test_no_name_entry_part(self):
        with self.admin_access.repo_cnx() as cnx:
            with self.assertRaises(dataimport.MissingTag) as cm:
                testutils.eac_import(cnx, self.datapath('no_name_entry_part.xml'))
            self.assertEqual(cm.exception.tag, 'part')
            self.assertEqual(cm.exception.tag_parent, 'nameEntry')


if __name__ == '__main__':
    unittest.main()
