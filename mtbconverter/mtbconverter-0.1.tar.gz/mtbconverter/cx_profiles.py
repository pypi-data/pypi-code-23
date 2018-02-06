"""Builder for CentraXX measure profile XML"""

import pyxb.utils.domutils
import xml.dom.minidom
from pyxb.namespace import XMLSchema_instance as xsi
from pyxb.namespace import XMLNamespaces as xmlns
import mtbconverter.cxxpy as cx
from . import cx_utils as cxu

SOMATIC_SNV_VERSION = 1.0
SOMATIC_CNV_VERSION = 1.0
SOMATIC_SV_VERSION = 1.0
GERMLINE_SNV_VERSION = 1.0
GERMLINE_CNV_VERSION = 1.0
METADATA_VERSION = 1.0

SNV_FIELD_TYPES = ["QBIC_chr", "QBIC_start", "QBIC_ref", "QBIC_alt", "QBIC_allele_frequency_tumor",
"QBIC_coverage", "QBIC_gene", "QBIC_base_change", "QBIC_aa_change", "QBIC_transcript", "QBIC_functional_class",
"QBIC_effect"]

GSNV_FIELD_TYPES = ["QBIC_chr", "QBIC_start", "QBIC_ref", "QBIC_alt", "QBIC_genotype",
"QBIC_gene", "QBIC_base_change", "QBIC_aa_change", "QBIC_transcript", "QBIC_functional_class",
"QBIC_effect"]

SCNV_FIELD_TYPES = ["QBIC_size", "QBIC_type", "QBIC_copy_number", "QBIC_gene", "QBIC_exons", "QBIC_transcript",
"QBIC_chr", "QBIC_start", "QBIC_end", "QBIC_effect"]

GCNV_FIELD_TYPES = ["QBIC_size", "QBIC_type", "QBIC_copy_number", "QBIC_gene", "QBIC_exons", "QBIC_transcript",
"QBIC_chr", "QBIC_start", "QBIC_end", "QBIC_effect"]

SV_FIELD_TYPES = ["QBIC_type", "QBIC_gene", "QBIC_effect", "QBIC_left_bp", "QBIC_right_bp"]

METADATA_TYPES = ["QBIC_diagnosis", "QBIC_tumor_content", "QBIC_pathogenic_germ", "QBIC_mutational_load",
"QBIC_chrom_instability", "QBIC_quality_flag", "QBIC_reference_genome"]

class SSNVProfiles():

    def __init__(self):
        pyxb.utils.domutils.BindingDOMSupport.DeclareNamespace(cx.Namespace, 'cxx')
        self._root = cx.CentraXXDataExchange()
        self._source = 'XML-IMPORT'
        self._catalogue_data = cx.CatalogueDataType()
        self._profile()
    
    def _profile(self):
        """Build the profile for somatic snvs"""
        flexible_data_set = cx.FlexibleDataSetType(
            Code="QBIC_SOMATIC_SNV_V{:.1f}".format(SOMATIC_SNV_VERSION),
            Systemwide="false",
            FlexibleDataSetType="MEASUREMENT",
            Category="LABOR")
        multi_lang_de = cx.MultilingualEntryType(Lang='de', Value='Somatic SNV V{:.1f}'.format(SOMATIC_SNV_VERSION))
        multi_lang_en = cx.MultilingualEntryType(Lang='en', Value='Somatic SNV V{:.1f}'.format(SOMATIC_SNV_VERSION))
        flexible_data_set.NameMultilingualEntries = [multi_lang_de, multi_lang_en]
    
        flexible_data_set.FlexibleValueComplexRefs = [
            cx.FlexibleValueRefType(FlexibleValueRef=field_type, Required="false") for field_type in SNV_FIELD_TYPES
        ]
        
        self._catalogue_data.append(flexible_data_set)

        cfr_template = cx.CrfTemplateType(Name='Somatic SNV V{:.1f}'.format(SOMATIC_SNV_VERSION),
            FlexibleDataSetRef='QBIC_SOMATIC_SNV_V{:.1f}'.format(SOMATIC_SNV_VERSION),
            TemplateType='LABORMETHOD', Version='{:.0f}'.format(SOMATIC_SNV_VERSION-1), EntityStatus='ACTIVE', Global='false', MultipleUse='false', Active='false')

        cfr_template_section = cx.CrfTemplateSectionType(Name='Somatic SNV V{:.1f}'.format(SOMATIC_SNV_VERSION),
            Height=len(SNV_FIELD_TYPES), Width='1', Position='-1')
        
        cfr_template_section.CrfTemplateField = [
            cx.CrfTemplateFieldType(LaborValue=value,
                LowerRow=ind,
                LowerColumn='0',
                UpperRow=ind,
                UpperColumn='0',
                Mandatory='false',
                VisibleCaption='true',
                FieldType='LABORVALUE') for ind, value in enumerate(SNV_FIELD_TYPES)]

        cfr_template.CrfTemplateSection = [cfr_template_section]

        self._catalogue_data.append(cfr_template)       
        
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


class GSNVProfiles():

    def __init__(self):
        pyxb.utils.domutils.BindingDOMSupport.DeclareNamespace(cx.Namespace, 'cxx')
        self._root = cx.CentraXXDataExchange()
        self._source = 'XML-IMPORT'
        self._catalogue_data = cx.CatalogueDataType()
        self._profile()
    
    def _profile(self):
        """Build the profile for germline snvs"""
        flexible_data_set = cx.FlexibleDataSetType(
            Code="QBIC_GERMLINE_SNV_V{:.1f}".format(GERMLINE_SNV_VERSION),
            Systemwide="false",
            FlexibleDataSetType="MEASUREMENT",
            Category="LABOR")
        multi_lang_de = cx.MultilingualEntryType(Lang='de', Value='Germline SNV V{:.1f}'.format(GERMLINE_SNV_VERSION))
        multi_lang_en = cx.MultilingualEntryType(Lang='en', Value='Germline SNV V{:.1f}'.format(GERMLINE_SNV_VERSION))
        flexible_data_set.NameMultilingualEntries = [multi_lang_de, multi_lang_en]      
    
        flexible_data_set.FlexibleValueComplexRefs = [
            cx.FlexibleValueRefType(FlexibleValueRef=field_type, Required="false") for field_type in GSNV_FIELD_TYPES
        ]
        
        self._catalogue_data.append(flexible_data_set)

        cfr_template = cx.CrfTemplateType(Name='Germline SNV V{:.1f}'.format(GERMLINE_SNV_VERSION),
            FlexibleDataSetRef='QBIC_GERMLINE_SNV_V{:.1f}'.format(GERMLINE_SNV_VERSION),
            TemplateType='LABORMETHOD', Version='{:.0f}'.format(GERMLINE_SNV_VERSION-1), EntityStatus='ACTIVE', Global='false', MultipleUse='false', Active='false')

        cfr_template_section = cx.CrfTemplateSectionType(Name='Germline SNV V{:.1f}'.format(GERMLINE_SNV_VERSION),
            Height=len(GSNV_FIELD_TYPES), Width='1', Position='-1')
        
        cfr_template_section.CrfTemplateField = [
            cx.CrfTemplateFieldType(LaborValue=value,
                LowerRow=ind,
                LowerColumn='0',
                UpperRow=ind,
                UpperColumn='0',
                Mandatory='false',
                VisibleCaption='true',
                FieldType='LABORVALUE') for ind, value in enumerate(GSNV_FIELD_TYPES)]

        cfr_template.CrfTemplateSection = [cfr_template_section]

        self._catalogue_data.append(cfr_template)       
        
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

class SCNVProfiles():

    def __init__(self):
        pyxb.utils.domutils.BindingDOMSupport.DeclareNamespace(cx.Namespace, 'cxx')
        self._root = cx.CentraXXDataExchange()
        self._source = 'XML-IMPORT'
        self._catalogue_data = cx.CatalogueDataType()
        self._profile()
    
    def _profile(self):
        """Build the profile for somatic cnvs"""
        flexible_data_set = cx.FlexibleDataSetType(
            Code="QBIC_SOMATIC_CNV_V{:.1f}".format(SOMATIC_CNV_VERSION),
            Systemwide="false",
            FlexibleDataSetType="MEASUREMENT",
            Category="LABOR")
        multi_lang_de = cx.MultilingualEntryType(Lang='de', Value='Somatic CNV V{:.1f}'.format(SOMATIC_CNV_VERSION))
        multi_lang_en = cx.MultilingualEntryType(Lang='en', Value='Somatic CNV V{:.1f}'.format(SOMATIC_CNV_VERSION))
        flexible_data_set.NameMultilingualEntries = [multi_lang_de, multi_lang_en]      
    
        flexible_data_set.FlexibleValueComplexRefs = [
            cx.FlexibleValueRefType(FlexibleValueRef=field_type, Required="false") for field_type in SCNV_FIELD_TYPES
        ]
        
        self._catalogue_data.append(flexible_data_set)

        cfr_template = cx.CrfTemplateType(Name='Somatic CNV V{:.1f}'.format(SOMATIC_CNV_VERSION),
            FlexibleDataSetRef='QBIC_SOMATIC_CNV_V{:.1f}'.format(SOMATIC_CNV_VERSION),
            TemplateType='LABORMETHOD', Version='{:.0f}'.format(SOMATIC_CNV_VERSION-1), EntityStatus='ACTIVE', Global='false', MultipleUse='false', Active='false')

        cfr_template_section = cx.CrfTemplateSectionType(Name='Somatic CNV V{:.1f}'.format(SOMATIC_CNV_VERSION),
            Height=len(GSNV_FIELD_TYPES), Width='1', Position='-1')
        
        cfr_template_section.CrfTemplateField = [
            cx.CrfTemplateFieldType(LaborValue=value,
                LowerRow=ind,
                LowerColumn='0',
                UpperRow=ind,
                UpperColumn='0',
                Mandatory='false',
                VisibleCaption='true',
                FieldType='LABORVALUE') for ind, value in enumerate(SCNV_FIELD_TYPES)]

        cfr_template.CrfTemplateSection = [cfr_template_section]

        self._catalogue_data.append(cfr_template)       
        
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

class GCNVProfiles():

    def __init__(self):
        pyxb.utils.domutils.BindingDOMSupport.DeclareNamespace(cx.Namespace, 'cxx')
        self._root = cx.CentraXXDataExchange()
        self._source = 'XML-IMPORT'
        self._catalogue_data = cx.CatalogueDataType()
        self._profile()
    
    def _profile(self):
        """Build the profile for germline cnvs"""
        flexible_data_set = cx.FlexibleDataSetType(
            Code="QBIC_GERMLINE_CNV_V{:.1f}".format(SOMATIC_CNV_VERSION),
            Systemwide="false",
            FlexibleDataSetType="MEASUREMENT",
            Category="LABOR")
        multi_lang_de = cx.MultilingualEntryType(Lang='de', Value='Germline CNV V{:.1f}'.format(GERMLINE_CNV_VERSION))
        multi_lang_en = cx.MultilingualEntryType(Lang='en', Value='Germline CNV V{:.1f}'.format(GERMLINE_CNV_VERSION))
        flexible_data_set.NameMultilingualEntries = [multi_lang_de, multi_lang_en]      
    
        flexible_data_set.FlexibleValueComplexRefs = [
            cx.FlexibleValueRefType(FlexibleValueRef=field_type, Required="false") for field_type in GCNV_FIELD_TYPES
        ]
        
        self._catalogue_data.append(flexible_data_set)

        cfr_template = cx.CrfTemplateType(Name='Germline CNV V{:.1f}'.format(GERMLINE_CNV_VERSION),
            FlexibleDataSetRef='QBIC_GERMLINE_CNV_V{:.1f}'.format(GERMLINE_CNV_VERSION),
            TemplateType='LABORMETHOD', Version='{:.0f}'.format(GERMLINE_CNV_VERSION-1), EntityStatus='ACTIVE', Global='false', MultipleUse='false', Active='false')

        cfr_template_section = cx.CrfTemplateSectionType(Name='Germline CNV V{:.1f}'.format(GERMLINE_CNV_VERSION),
            Height=len(GCNV_FIELD_TYPES), Width='1', Position='-1')
        
        cfr_template_section.CrfTemplateField = [
            cx.CrfTemplateFieldType(LaborValue=value,
                LowerRow=ind,
                LowerColumn='0',
                UpperRow=ind,
                UpperColumn='0',
                Mandatory='false',
                VisibleCaption='true',
                FieldType='LABORVALUE') for ind, value in enumerate(GCNV_FIELD_TYPES)]

        cfr_template.CrfTemplateSection = [cfr_template_section]

        self._catalogue_data.append(cfr_template)       
        
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

class SVProfiles():

    def __init__(self):
        pyxb.utils.domutils.BindingDOMSupport.DeclareNamespace(cx.Namespace, 'cxx')
        self._root = cx.CentraXXDataExchange()
        self._source = 'XML-IMPORT'
        self._catalogue_data = cx.CatalogueDataType()
        self._profile()
    
    def _profile(self):
        """Build the profile for somatic structural variants"""
        flexible_data_set = cx.FlexibleDataSetType(
            Code="QBIC_SOMATIC_SV_V{:.1f}".format(SOMATIC_SV_VERSION),
            Systemwide="false",
            FlexibleDataSetType="MEASUREMENT",
            Category="LABOR")
        multi_lang_de = cx.MultilingualEntryType(Lang='de', Value='Somatic SV V{:.1f}'.format(SOMATIC_SV_VERSION))
        multi_lang_en = cx.MultilingualEntryType(Lang='en', Value='Somatic SV V{:.1f}'.format(SOMATIC_SV_VERSION))
        flexible_data_set.NameMultilingualEntries = [multi_lang_de, multi_lang_en]      
    
        flexible_data_set.FlexibleValueComplexRefs = [
            cx.FlexibleValueRefType(FlexibleValueRef=field_type, Required="false") for field_type in SV_FIELD_TYPES
        ]
        
        self._catalogue_data.append(flexible_data_set)

        cfr_template = cx.CrfTemplateType(Name='Somatic SV V{:.1f}'.format(SOMATIC_SV_VERSION),
            FlexibleDataSetRef='QBIC_SOMATIC_SV_V{:.1f}'.format(SOMATIC_SV_VERSION),
            TemplateType='LABORMETHOD', Version='{:.0f}'.format(SOMATIC_SV_VERSION-1), EntityStatus='ACTIVE', Global='false', MultipleUse='false', Active='false')

        cfr_template_section = cx.CrfTemplateSectionType(Name='Somatic SV V{:.1f}'.format(SOMATIC_SV_VERSION),
            Height=len(SV_FIELD_TYPES), Width='1', Position='-1')
        
        cfr_template_section.CrfTemplateField = [
            cx.CrfTemplateFieldType(LaborValue=value,
                LowerRow=ind,
                LowerColumn='0',
                UpperRow=ind,
                UpperColumn='0',
                Mandatory='false',
                VisibleCaption='true',
                FieldType='LABORVALUE') for ind, value in enumerate(SV_FIELD_TYPES)]

        cfr_template.CrfTemplateSection = [cfr_template_section]

        self._catalogue_data.append(cfr_template)       
        
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

class MetadataProfiles():

    def __init__(self):
        pyxb.utils.domutils.BindingDOMSupport.DeclareNamespace(cx.Namespace, 'cxx')
        self._root = cx.CentraXXDataExchange()
        self._source = 'XML-IMPORT'
        self._catalogue_data = cx.CatalogueDataType()
        self._profile()
    
    def _profile(self):
        """Build the profile for metadata information"""
        flexible_data_set = cx.FlexibleDataSetType(
            Code="QBIC_METADATA_V{:.1f}".format(METADATA_VERSION),
            Systemwide="false",
            FlexibleDataSetType="MEASUREMENT",
            Category="LABOR")
        multi_lang_de = cx.MultilingualEntryType(Lang='de', Value='Metadata V{:.1f}'.format(METADATA_VERSION))
        multi_lang_en = cx.MultilingualEntryType(Lang='en', Value='Metadata V{:.1f}'.format(METADATA_VERSION))
        flexible_data_set.NameMultilingualEntries = [multi_lang_de, multi_lang_en]      
    
        flexible_data_set.FlexibleValueComplexRefs = [
            cx.FlexibleValueRefType(FlexibleValueRef=field_type, Required="false") for field_type in METADATA_TYPES
        ]
        
        self._catalogue_data.append(flexible_data_set)

        cfr_template = cx.CrfTemplateType(Name='Metadata V{:.1f}'.format(METADATA_VERSION),
            FlexibleDataSetRef='QBIC_METADATA_V{:.1f}'.format(METADATA_VERSION),
            TemplateType='LABORMETHOD', Version='{:.0f}'.format(METADATA_VERSION-1), EntityStatus='ACTIVE', Global='false', MultipleUse='false', Active='false')

        cfr_template_section = cx.CrfTemplateSectionType(Name='Metadata V{:.1f}'.format(METADATA_VERSION),
            Height=len(METADATA_TYPES), Width='1', Position='-1')
        
        cfr_template_section.CrfTemplateField = [
            cx.CrfTemplateFieldType(LaborValue=value,
                LowerRow=ind,
                LowerColumn='0',
                UpperRow=ind,
                UpperColumn='0',
                Mandatory='false',
                VisibleCaption='true',
                FieldType='LABORVALUE') for ind, value in enumerate(METADATA_TYPES)]

        cfr_template.CrfTemplateSection = [cfr_template_section]

        self._catalogue_data.append(cfr_template)       
        
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


