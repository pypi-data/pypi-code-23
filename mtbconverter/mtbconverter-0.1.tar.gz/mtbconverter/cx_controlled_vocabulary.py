"""Builder for controlled vocabulary XML as part of the preparation
for the CentraXX import"""

import pyxb.utils.domutils
import xml.dom.minidom
from pyxb.namespace import XMLSchema_instance as xsi
from pyxb.namespace import XMLNamespaces as xmlns
import mtbconverter.cxxpy as cx
from mtbparser.snv_utils import SSnvHeader
from . import cx_utils as cxu

CV_VERSION = '0.1'

class ControlledVocabulary:
    
    def __init__(self):
        pyxb.utils.domutils.BindingDOMSupport.DeclareNamespace(cx.Namespace, 'cxx')
        self._root = cx.CentraXXDataExchange()
        self._source = 'XML-IMPORT'
        self._catalogue_data = cx.CatalogueDataType()
        self._cvforssnv()
    
    def _cvforssnv(self):
        """Create the XML entries for the
        somatic SNVs information"""

        # register the chromosomes (de, en)
        for chr_index in cxu.CV_CHROMOSOMES:
            multi_entry_type_de = cx.MultilingualEntryType(Lang='de', Value='Chromosome {}{}{}'.format(cxu.CV_PREFIX, 'chr',chr_index))
            multi_entry_type_en = cx.MultilingualEntryType(Lang='en', Value='Chromosome {}{}{}'.format(cxu.CV_PREFIX, 'chr',chr_index))
            item = cx.UsageEntryType()
            item.NameMultilingualEntries = [multi_entry_type_de, multi_entry_type_en]
            item.Code = '{}{}{}'.format(cxu.CV_PREFIX, 'chr',chr_index)
            item.Category = "false"
            self._catalogue_data.append(item)
        
        # create vc for sSNV effects
        for effect in cxu.CV_EFFECT_SSNV:
            multi_entry_type_de = cx.MultilingualEntryType(Lang='de', Value='{}{}'.format(cxu.CV_PREFIX, effect))
            multi_entry_type_en = cx.MultilingualEntryType(Lang='en', Value='{}{}'.format(cxu.CV_PREFIX, effect))
            item = cx.UsageEntryType()
            item.NameMultilingualEntries = [multi_entry_type_de, multi_entry_type_en]
            item.Code = '{}{}'.format(cxu.CV_PREFIX, effect)
            item.Category = "false"
            self._catalogue_data.append(item)
        
        # create cv for bases
        for base in cxu.CV_BASES:
            multi_entry_type_de = cx.MultilingualEntryType(Lang='de', Value='{}{}{}'.format(cxu.CV_PREFIX, 'base', base))
            multi_entry_type_en = cx.MultilingualEntryType(Lang='en', Value='{}{}{}'.format(cxu.CV_PREFIX, 'base', base))
            item = cx.UsageEntryType()
            item.NameMultilingualEntries = [multi_entry_type_de, multi_entry_type_en]
            item.Code = '{}{}{}'.format(cxu.CV_PREFIX, 'base', base)
            item.Category = "false"
            self._catalogue_data.append(item)
        
        # create cv for mutational load
        for load in cxu.CV_MUT_LOAD:
            multi_entry_type_de = cx.MultilingualEntryType(Lang='de', Value='{}{}_{}'.format(cxu.CV_PREFIX, 'mutational_load', load))
            multi_entry_type_en = cx.MultilingualEntryType(Lang='en', Value='{}{}_{}'.format(cxu.CV_PREFIX, 'mutational_load', load))
            item = cx.UsageEntryType()
            item.NameMultilingualEntries = [multi_entry_type_de, multi_entry_type_en]
            item.Code = '{}{}_{}'.format(cxu.CV_PREFIX, 'mutational_load', load)
            item.Category = "false"
            self._catalogue_data.append(item)
        
        for genotype in cxu.CV_GENOTYPES:
            multi_entry_type_de = cx.MultilingualEntryType(Lang='de', Value='{}{}_{}'.format(cxu.CV_PREFIX, 'genotype', genotype))
            multi_entry_type_en = cx.MultilingualEntryType(Lang='en', Value='{}{}_{}'.format(cxu.CV_PREFIX, 'genotype', genotype))
            item = cx.UsageEntryType()
            item.NameMultilingualEntries = [multi_entry_type_de, multi_entry_type_en]
            item.Code = '{}{}_{}'.format(cxu.CV_PREFIX, 'genotype', genotype)
            item.Category = "false"
            self._catalogue_data.append(item)

        
    def getXML(self):
        """Write the XML object into an XML
        file"""
        self._root.Source = self._source
        self._root.CatalogueData = self._catalogue_data
        root_dom = self._root.toDOM()
        root_dom.documentElement.setAttributeNS(
            xsi.uri(), 'xsi:schemaLocation',
            'http://www.kairos-med.de ../CentraXXExchange.xsd')
        root_dom.documentElement.setAttributeNS(
            xmlns.uri(), 'xmlns:xsi', xsi.uri())
        return root_dom.toprettyxml(encoding='utf-8')

