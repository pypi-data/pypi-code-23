"""Builder for CentraXX parameters XML"""

import pyxb.utils.domutils
import xml.dom.minidom
from pyxb.namespace import XMLSchema_instance as xsi
from pyxb.namespace import XMLNamespaces as xmlns
import mtbconverter.cxxpy as cx
from . import cx_utils as cxu

class Parameters():

    def __init__(self):
        pyxb.utils.domutils.BindingDOMSupport.DeclareNamespace(cx.Namespace, 'cxx')
        self._root = cx.CentraXXDataExchange()
        self._source = 'XML-IMPORT'
        self._catalogue_data = cx.CatalogueDataType()
        self._params()
    
    def _params(self):
        """Call methods for the parameter definition"""
        flexible_value_ci = cx.FlexibleValuesType()

        # Add column fields for MTB variant report
        self._addchromosomes(flexible_value_ci)
        self._addcopynumber(flexible_value_ci)
        self._addeffects(flexible_value_ci)
        self._addstart(flexible_value_ci)
        self._addref(flexible_value_ci)
        self._addalt(flexible_value_ci)
        self._addallelefreq(flexible_value_ci)
        self._addcoverage(flexible_value_ci)
        self._addgene(flexible_value_ci)
        self._addbasechange(flexible_value_ci)
        self._addaachange(flexible_value_ci)
        self._addtranscript(flexible_value_ci)
        self._addfunctionalclass(flexible_value_ci)
        self._addmutationalload(flexible_value_ci)
        self._addgenotype(flexible_value_ci)
        self._addeffects_germline(flexible_value_ci)
        self._addexons(flexible_value_ci)
        self._addend(flexible_value_ci)
        self._addtype(flexible_value_ci)
        self._addleftbp(flexible_value_ci)
        self._addrightbp(flexible_value_ci)
        self._adddiagnosis(flexible_value_ci)
        self._addtumorcontent(flexible_value_ci)
        self._addpathogenicinfo(flexible_value_ci)
        self._addchromosomalinstability(flexible_value_ci)
        self._addqualityflags(flexible_value_ci)
        self._addreferencegenome(flexible_value_ci)
        self._addsize(flexible_value_ci)

        # Append the flexible values to the catalogue data
        self._catalogue_data.append(flexible_value_ci)

    def _addsize(self, flexible_value_ci):
        """Add CNV size information"""
        flex_type = cx.FlexibleStringType()
        flex_type.Code = "{}size".format(cxu.CV_PREFIX)
        flex_type.Name = "CNV size"
        flex_type.ShortName = "Size"
        flex_type.Description = "Copy number variation size."

        multi_entry_type_de = cx.MultilingualEntryType(Lang='de', Value='size')
        multi_entry_type_en = cx.MultilingualEntryType(Lang='en', Value='size')
        multi_entry_type_de_desc = cx.MultilingualEntryType(Lang='de', Value='size')
        multi_entry_type_en_desc = cx.MultilingualEntryType(Lang='en', Value='size')

        flex_type.NameMultilingualEntries = [multi_entry_type_de, multi_entry_type_en]
        flex_type.DescMultilingualEntries = [multi_entry_type_de_desc, multi_entry_type_en_desc]

        flexible_value_ci.append(flex_type)


    def _addcopynumber(self, flexible_value_ci):
        """Add copy number info"""
        flex_type = cx.FlexibleStringType()
        flex_type.Code = "{}copy_number".format(cxu.CV_PREFIX)
        flex_type.Name = "Copy number"
        flex_type.ShortName = "Copy number"
        flex_type.Description = "Copy number amount."

        multi_entry_type_de = cx.MultilingualEntryType(Lang='de', Value='copy_number')
        multi_entry_type_en = cx.MultilingualEntryType(Lang='en', Value='copy_number')
        multi_entry_type_de_desc = cx.MultilingualEntryType(Lang='de', Value='copy_number')
        multi_entry_type_en_desc = cx.MultilingualEntryType(Lang='en', Value='copy_number')

        flex_type.NameMultilingualEntries = [multi_entry_type_de, multi_entry_type_en]
        flex_type.DescMultilingualEntries = [multi_entry_type_de_desc, multi_entry_type_en_desc]

        flexible_value_ci.append(flex_type)

    def _addreferencegenome(self, flexible_value_ci):
        """Add reference genome info"""
        flex_type = cx.FlexibleStringType()
        flex_type.Code = "{}reference_genome".format(cxu.CV_PREFIX)
        flex_type.Name = "Reference genome"
        flex_type.ShortName = "Ref. genome"
        flex_type.Description = "Reference genome used for mapping."

        multi_entry_type_de = cx.MultilingualEntryType(Lang='de', Value='reference_genome')
        multi_entry_type_en = cx.MultilingualEntryType(Lang='en', Value='reference_genome')
        multi_entry_type_de_desc = cx.MultilingualEntryType(Lang='de', Value='reference_genome')
        multi_entry_type_en_desc = cx.MultilingualEntryType(Lang='en', Value='reference_genome')

        flex_type.NameMultilingualEntries = [multi_entry_type_de, multi_entry_type_en]
        flex_type.DescMultilingualEntries = [multi_entry_type_de_desc, multi_entry_type_en_desc]

        flexible_value_ci.append(flex_type)
    
    def _addqualityflags(self, flexible_value_ci):
        """Add quality flags info"""
        flex_type = cx.FlexibleStringType()
        flex_type.Code = "{}quality_flag".format(cxu.CV_PREFIX)
        flex_type.Name = "Quality flags"
        flex_type.ShortName = "Quality flags"
        flex_type.Description = "Quality flags information."

        multi_entry_type_de = cx.MultilingualEntryType(Lang='de', Value='quality_flag')
        multi_entry_type_en = cx.MultilingualEntryType(Lang='en', Value='quality_flag')
        multi_entry_type_de_desc = cx.MultilingualEntryType(Lang='de', Value='quality_flag')
        multi_entry_type_en_desc = cx.MultilingualEntryType(Lang='en', Value='quality_flag')

        flex_type.NameMultilingualEntries = [multi_entry_type_de, multi_entry_type_en]
        flex_type.DescMultilingualEntries = [multi_entry_type_de_desc, multi_entry_type_en_desc]

        flexible_value_ci.append(flex_type)

    def _addchromosomalinstability(self, flexible_value_ci):
        """Add chromosomal instability info"""
        flex_type = cx.FlexibleStringType()
        flex_type.Code = "{}chrom_instability".format(cxu.CV_PREFIX)
        flex_type.Name = "Chromosomal instability"
        flex_type.ShortName = "Chr. instab."
        flex_type.Description = "Chromosomal instability information."

        multi_entry_type_de = cx.MultilingualEntryType(Lang='de', Value='chrom_instability')
        multi_entry_type_en = cx.MultilingualEntryType(Lang='en', Value='chrom_instability')
        multi_entry_type_de_desc = cx.MultilingualEntryType(Lang='de', Value='chrom_instability')
        multi_entry_type_en_desc = cx.MultilingualEntryType(Lang='en', Value='chrom_instability')

        flex_type.NameMultilingualEntries = [multi_entry_type_de, multi_entry_type_en]
        flex_type.DescMultilingualEntries = [multi_entry_type_de_desc, multi_entry_type_en_desc]

        flexible_value_ci.append(flex_type)

    def _addpathogenicinfo(self, flexible_value_ci):
        """Add field for pathogenic germline info"""
        flex_type = cx.FlexibleStringType()
        flex_type.Code = "{}pathogenic_germ".format(cxu.CV_PREFIX)
        flex_type.Name = "Pathogenic germline"
        flex_type.ShortName = "Path. germline"
        flex_type.Description = "Presence of pathogenic germline information."

        multi_entry_type_de = cx.MultilingualEntryType(Lang='de', Value='pathogenic_germ')
        multi_entry_type_en = cx.MultilingualEntryType(Lang='en', Value='pathogenic_germ')
        multi_entry_type_de_desc = cx.MultilingualEntryType(Lang='de', Value='pathogenic_germ')
        multi_entry_type_en_desc = cx.MultilingualEntryType(Lang='en', Value='pathogenic_germ')

        flex_type.NameMultilingualEntries = [multi_entry_type_de, multi_entry_type_en]
        flex_type.DescMultilingualEntries = [multi_entry_type_de_desc, multi_entry_type_en_desc]

        flexible_value_ci.append(flex_type)

    def _addtumorcontent(self, flexible_value_ci):
        """Add field for tumor content"""
        flex_type = cx.FlexibleDecimalType()
        flex_type.Code = "{}tumor_content".format(cxu.CV_PREFIX)
        flex_type.Name = "Sample tumor content"
        flex_type.ShortName = "Tumor content"
        flex_type.Description = "Tumor content of the sample as reportet by the pathologist."

        multi_entry_type_de = cx.MultilingualEntryType(Lang='de', Value='tumor_content')
        multi_entry_type_en = cx.MultilingualEntryType(Lang='en', Value='tumor_content')
        multi_entry_type_de_desc = cx.MultilingualEntryType(Lang='de', Value='tumor_content')
        multi_entry_type_en_desc = cx.MultilingualEntryType(Lang='en', Value='tumor_content')

        flex_type.NameMultilingualEntries = [multi_entry_type_de, multi_entry_type_en]
        flex_type.DescMultilingualEntries = [multi_entry_type_de_desc, multi_entry_type_en_desc]

        flexible_value_ci.append(flex_type)

    def _adddiagnosis(self, flexible_value_ci):
        """Add field for diagnosis terms"""
        flex_type = cx.FlexibleStringType()
        flex_type.Code = "{}diagnosis".format(cxu.CV_PREFIX)
        flex_type.Name = "Diagnosis"
        flex_type.ShortName = "Diagnosis"
        flex_type.Description = "Diagnosis based on the variant data"

        multi_entry_type_de = cx.MultilingualEntryType(Lang='de', Value='diagnosis')
        multi_entry_type_en = cx.MultilingualEntryType(Lang='en', Value='diagnosis')
        multi_entry_type_de_desc = cx.MultilingualEntryType(Lang='de', Value='diagnosis')
        multi_entry_type_en_desc = cx.MultilingualEntryType(Lang='en', Value='diagnosis')

        flex_type.NameMultilingualEntries = [multi_entry_type_de, multi_entry_type_en]
        flex_type.DescMultilingualEntries = [multi_entry_type_de_desc, multi_entry_type_en_desc]

        flexible_value_ci.append(flex_type)

    def _addleftbp(self, flexible_value_ci):
        """Add field for left break point position of structural
        variant"""
        flex_type = cx.FlexibleStringType()
        flex_type.Code = "{}left_bp".format(cxu.CV_PREFIX)
        flex_type.Name = "Left break point position"
        flex_type.ShortName = "SV left bp"
        flex_type.Description = "Left break point position of SV"

        multi_entry_type_de = cx.MultilingualEntryType(Lang='de', Value='left_bp')
        multi_entry_type_en = cx.MultilingualEntryType(Lang='en', Value='left_bp')
        multi_entry_type_de_desc = cx.MultilingualEntryType(Lang='de', Value='left_bp')
        multi_entry_type_en_desc = cx.MultilingualEntryType(Lang='en', Value='left_bp')

        flex_type.NameMultilingualEntries = [multi_entry_type_de, multi_entry_type_en]
        flex_type.DescMultilingualEntries = [multi_entry_type_de_desc, multi_entry_type_en_desc]

        flexible_value_ci.append(flex_type)

    def _addrightbp(self, flexible_value_ci):
        """Add field for right break point position of structural
        variant"""
        flex_type = cx.FlexibleStringType()
        flex_type.Code = "{}right_bp".format(cxu.CV_PREFIX)
        flex_type.Name = "LRighteft break point position"
        flex_type.ShortName = "SV right bp"
        flex_type.Description = "Right break point position of SV"

        multi_entry_type_de = cx.MultilingualEntryType(Lang='de', Value='right_bp')
        multi_entry_type_en = cx.MultilingualEntryType(Lang='en', Value='right_bp')
        multi_entry_type_de_desc = cx.MultilingualEntryType(Lang='de', Value='right_bp')
        multi_entry_type_en_desc = cx.MultilingualEntryType(Lang='en', Value='right_bp')

        flex_type.NameMultilingualEntries = [multi_entry_type_de, multi_entry_type_en]
        flex_type.DescMultilingualEntries = [multi_entry_type_de_desc, multi_entry_type_en_desc]

        flexible_value_ci.append(flex_type)
    
    def _addtype(self, flexible_value_ci):
        """Add type field for structural variants"""
        flex_type = cx.FlexibleStringType()
        flex_type.Code = "{}type".format(cxu.CV_PREFIX)
        flex_type.Name = "Type of structural variant"
        flex_type.ShortName = "SV type"
        flex_type.Description = "Type of structural variant"

        multi_entry_type_de = cx.MultilingualEntryType(Lang='de', Value='type')
        multi_entry_type_en = cx.MultilingualEntryType(Lang='en', Value='type')
        multi_entry_type_de_desc = cx.MultilingualEntryType(Lang='de', Value='type')
        multi_entry_type_en_desc = cx.MultilingualEntryType(Lang='en', Value='type')

        flex_type.NameMultilingualEntries = [multi_entry_type_de, multi_entry_type_en]
        flex_type.DescMultilingualEntries = [multi_entry_type_de_desc, multi_entry_type_en_desc]

        flexible_value_ci.append(flex_type)

    def _addend(self, flexible_value_ci):
        """Add a field for end positions of CNVs"""
        flex_type = cx.FlexibleIntegerType()
        flex_type.Code = "{}end".format(cxu.CV_PREFIX)
        flex_type.Name = "End position of CNV"
        flex_type.ShortName = "End pos."
        flex_type.Description = "End position of CNV"

        multi_entry_type_de = cx.MultilingualEntryType(Lang='de', Value='end')
        multi_entry_type_en = cx.MultilingualEntryType(Lang='en', Value='end')
        multi_entry_type_de_desc = cx.MultilingualEntryType(Lang='de', Value='end')
        multi_entry_type_en_desc = cx.MultilingualEntryType(Lang='en', Value='end')

        flex_type.NameMultilingualEntries = [multi_entry_type_de, multi_entry_type_en]
        flex_type.DescMultilingualEntries = [multi_entry_type_de_desc, multi_entry_type_en_desc]

        flexible_value_ci.append(flex_type)
    
    def _addexons(self, flexible_value_ci):
        """Add the exon description field"""
        flex_type = cx.FlexibleStringType()
        flex_type.Code = "{}exons".format(cxu.CV_PREFIX)
        flex_type.Name = "Name the affected exons of CNV"
        flex_type.ShortName = "Exons affected by CNV"
        flex_type.Description = "Exons affected by CNV"

        multi_entry_type_de = cx.MultilingualEntryType(Lang='de', Value='exons')
        multi_entry_type_en = cx.MultilingualEntryType(Lang='en', Value='exons')
        multi_entry_type_de_desc = cx.MultilingualEntryType(Lang='de', Value='exons')
        multi_entry_type_en_desc = cx.MultilingualEntryType(Lang='en', Value='exons')

        flex_type.NameMultilingualEntries = [multi_entry_type_de, multi_entry_type_en]
        flex_type.DescMultilingualEntries = [multi_entry_type_de_desc, multi_entry_type_en_desc]

        flexible_value_ci.append(flex_type)

    def _addeffects_germline(self, flexible_value_ci):
        """Add the effects for germline SNVs"""
        flex_type = cx.FlexibleStringType()
        flex_type.Code = "{}effect_germline".format(cxu.CV_PREFIX)
        flex_type.Name = "Effect prediction in germline SNV"
        flex_type.ShortName = "Pred. germline effect"
        flex_type.Description = "ACMG-based effect of variant"

        multi_entry_type_de = cx.MultilingualEntryType(Lang='de', Value='effect_germline')
        multi_entry_type_en = cx.MultilingualEntryType(Lang='en', Value='effect_germline')
        multi_entry_type_de_desc = cx.MultilingualEntryType(Lang='de', Value='effect_germline')
        multi_entry_type_en_desc = cx.MultilingualEntryType(Lang='en', Value='effect_germline')

        flex_type.NameMultilingualEntries = [multi_entry_type_de, multi_entry_type_en]
        flex_type.DescMultilingualEntries = [multi_entry_type_de_desc, multi_entry_type_en_desc]

        flexible_value_ci.append(flex_type)
        
    def _addgenotype(self, flexible_value_ci):
        """Mutational genotype enumeration """
        flex_enum_value = cx.FlexibleEnumerationType()
        flex_enum_value.Code = "{}genotype".format(cxu.CV_PREFIX)
        flex_enum_value.Name = "Genotype"
        flex_enum_value.ShortName = "Genotype"
        flex_enum_value.ChoiseType = "SELECTONE"
        flex_enum_value.Description = "Enumeration of different genotypes"

        multi_entry_type_de = cx.MultilingualEntryType(Lang='de', Value='genotype')
        multi_entry_type_en = cx.MultilingualEntryType(Lang='en', Value='genotype')
        multi_entry_type_de_desc = cx.MultilingualEntryType(Lang='de', Value='genotype')
        multi_entry_type_en_desc = cx.MultilingualEntryType(Lang='en', Value='genotype')

        flex_enum_value.NameMultilingualEntries = [multi_entry_type_de, multi_entry_type_en]
        flex_enum_value.DescMultilingualEntries = [multi_entry_type_de_desc, multi_entry_type_en_desc]

        flex_enum_value.UsageEntryTypeRef = ["{}{}_{}".format(cxu.CV_PREFIX, 'genotype', genotype) for genotype in cxu.CV_GENOTYPES]
        flexible_value_ci.append(flex_enum_value)

    def _addmutationalload(self, flexible_value_ci):
        """Mutational load enumeration 'low', 'medium', 'high'"""
        flex_enum_value = cx.FlexibleEnumerationType()
        flex_enum_value.Code = "{}mutational_load".format(cxu.CV_PREFIX)
        flex_enum_value.Name = "Mutational load"
        flex_enum_value.ShortName = "Mut. load"
        flex_enum_value.ChoiseType = "SELECTONE"
        flex_enum_value.Description = "Enumeration of different mutational load flags"

        multi_entry_type_de = cx.MultilingualEntryType(Lang='de', Value='load')
        multi_entry_type_en = cx.MultilingualEntryType(Lang='en', Value='load')
        multi_entry_type_de_desc = cx.MultilingualEntryType(Lang='de', Value='load')
        multi_entry_type_en_desc = cx.MultilingualEntryType(Lang='en', Value='load')

        flex_enum_value.NameMultilingualEntries = [multi_entry_type_de, multi_entry_type_en]
        flex_enum_value.DescMultilingualEntries = [multi_entry_type_de_desc, multi_entry_type_en_desc]

        flex_enum_value.UsageEntryTypeRef = ["{}{}_{}".format(cxu.CV_PREFIX, 'mutational_load', load) for load in cxu.CV_MUT_LOAD]
        flexible_value_ci.append(flex_enum_value)
    
    def _addstart(self, flexible_value_ci):
        """Add the start position of the somatic SNV"""
        flex_type = cx.FlexibleIntegerType()
        flex_type.Code = "{}start".format(cxu.CV_PREFIX)
        flex_type.Name = "Start of SNV"
        flex_type.ShortName = "Start"
        flex_type.Description = "Start position of SNV"

        multi_entry_type_de = cx.MultilingualEntryType(Lang='de', Value='start')
        multi_entry_type_en = cx.MultilingualEntryType(Lang='en', Value='start')
        multi_entry_type_de_desc = cx.MultilingualEntryType(Lang='de', Value='start')
        multi_entry_type_en_desc = cx.MultilingualEntryType(Lang='en', Value='start')

        flex_type.NameMultilingualEntries = [multi_entry_type_de, multi_entry_type_en]
        flex_type.DescMultilingualEntries = [multi_entry_type_de_desc, multi_entry_type_en_desc]

        flexible_value_ci.append(flex_type)

    def _addref(self, flexible_value_ci):
        """Adds the reference base enumeration"""
        flex_enum_value = cx.FlexibleEnumerationType()
        flex_enum_value.Code = "{}ref".format(cxu.CV_PREFIX)
        flex_enum_value.Name = "Reference base"
        flex_enum_value.ShortName = "Reference"
        flex_enum_value.ChoiseType = "SELECTONE"
        flex_enum_value.Description = "Enumeration of different reference bases"

        multi_entry_type_de = cx.MultilingualEntryType(Lang='de', Value='ref')
        multi_entry_type_en = cx.MultilingualEntryType(Lang='en', Value='ref')
        multi_entry_type_de_desc = cx.MultilingualEntryType(Lang='de', Value='ref')
        multi_entry_type_en_desc = cx.MultilingualEntryType(Lang='en', Value='ref')

        flex_enum_value.NameMultilingualEntries = [multi_entry_type_de, multi_entry_type_en]
        flex_enum_value.DescMultilingualEntries = [multi_entry_type_de_desc, multi_entry_type_en_desc]

        flex_enum_value.UsageEntryTypeRef = ["{}{}{}".format(cxu.CV_PREFIX, 'base', ref) for ref in cxu.CV_BASES]
        flexible_value_ci.append(flex_enum_value)
    
    def _addalt(self, flexible_value_ci):
        """Add the start position of the somatic SNV"""
        flex_type = cx.FlexibleStringType()
        flex_type.Code = "{}alt".format(cxu.CV_PREFIX)
        flex_type.Name = "Alternative"
        flex_type.ShortName = "Alt"
        flex_type.Description = "Alternative bases in the variant"

        multi_entry_type_de = cx.MultilingualEntryType(Lang='de', Value='alt')
        multi_entry_type_en = cx.MultilingualEntryType(Lang='en', Value='alt')
        multi_entry_type_de_desc = cx.MultilingualEntryType(Lang='de', Value='alt')
        multi_entry_type_en_desc = cx.MultilingualEntryType(Lang='en', Value='alt')

        flex_type.NameMultilingualEntries = [multi_entry_type_de, multi_entry_type_en]
        flex_type.DescMultilingualEntries = [multi_entry_type_de_desc, multi_entry_type_en_desc]

        flexible_value_ci.append(flex_type)

    
    def _addallelefreq(self, flexible_value_ci):
        """Add the alle frequency parameter"""
        flex_type = cx.FlexibleDecimalType()
        flex_type.Code = "{}allele_frequency_tumor".format(cxu.CV_PREFIX)
        flex_type.Name = "Allele Frequency Tumor"
        flex_type.ShortName = "Allele Frequency"
        flex_type.Description = "The allele frequency of the variant in the tumor sample"

        multi_entry_type_de = cx.MultilingualEntryType(Lang='de', Value='allele_frequency_tumor')
        multi_entry_type_en = cx.MultilingualEntryType(Lang='en', Value='allele_frequency_tumor')
        multi_entry_type_de_desc = cx.MultilingualEntryType(Lang='de', Value='allele_frequency_tumor')
        multi_entry_type_en_desc = cx.MultilingualEntryType(Lang='en', Value='allele_frequency_tumor')

        flex_type.NameMultilingualEntries = [multi_entry_type_de, multi_entry_type_en]
        flex_type.DescMultilingualEntries = [multi_entry_type_de_desc, multi_entry_type_en_desc]

        flexible_value_ci.append(flex_type)

    def _addcoverage(self, flexible_value_ci):
        """Add the coverage information"""
        flex_type = cx.FlexibleDecimalType()
        flex_type.Code = "{}coverage".format(cxu.CV_PREFIX)
        flex_type.Name = "Coverage"
        flex_type.ShortName = "Coverage"
        flex_type.Description = "Variant coverage information"

        multi_entry_type_de = cx.MultilingualEntryType(Lang='de', Value='coverage')
        multi_entry_type_en = cx.MultilingualEntryType(Lang='en', Value='coverage')
        multi_entry_type_de_desc = cx.MultilingualEntryType(Lang='de', Value='coverage')
        multi_entry_type_en_desc = cx.MultilingualEntryType(Lang='en', Value='coverage')

        flex_type.NameMultilingualEntries = [multi_entry_type_de, multi_entry_type_en]
        flex_type.DescMultilingualEntries = [multi_entry_type_de_desc, multi_entry_type_en_desc]

        flexible_value_ci.append(flex_type)
    
    def _addgene(self, flexible_value_ci):
        """Add the gene name"""
        flex_type = cx.FlexibleStringType()
        flex_type.Code = "{}gene".format(cxu.CV_PREFIX)
        flex_type.Name = "Gene Name"
        flex_type.ShortName = "Gene"
        flex_type.Description = "The affected gene"

        multi_entry_type_de = cx.MultilingualEntryType(Lang='de', Value='gene')
        multi_entry_type_en = cx.MultilingualEntryType(Lang='en', Value='gene')
        multi_entry_type_de_desc = cx.MultilingualEntryType(Lang='de', Value='gene')
        multi_entry_type_en_desc = cx.MultilingualEntryType(Lang='en', Value='gene')

        flex_type.NameMultilingualEntries = [multi_entry_type_de, multi_entry_type_en]
        flex_type.DescMultilingualEntries = [multi_entry_type_de_desc, multi_entry_type_en_desc]

        flexible_value_ci.append(flex_type)

    
    def _addbasechange(self, flexible_value_ci):
        """Add the base change info"""
        flex_type = cx.FlexibleStringType()
        flex_type.Code = "{}base_change".format(cxu.CV_PREFIX)
        flex_type.Name = "Base change"
        flex_type.ShortName = "base change"
        flex_type.Description = "Base change info in HGVS terms"

        multi_entry_type_de = cx.MultilingualEntryType(Lang='de', Value='base_change')
        multi_entry_type_en = cx.MultilingualEntryType(Lang='en', Value='base_change')
        multi_entry_type_de_desc = cx.MultilingualEntryType(Lang='de', Value='base_change')
        multi_entry_type_en_desc = cx.MultilingualEntryType(Lang='en', Value='base_change')

        flex_type.NameMultilingualEntries = [multi_entry_type_de, multi_entry_type_en]
        flex_type.DescMultilingualEntries = [multi_entry_type_de_desc, multi_entry_type_en_desc]

        flexible_value_ci.append(flex_type)
    
    def _addaachange(self, flexible_value_ci):
        """Add the aa change info"""
        flex_type = cx.FlexibleStringType()
        flex_type.Code = "{}aa_change".format(cxu.CV_PREFIX)
        flex_type.Name = "Aminoacid change"
        flex_type.ShortName = "AA change"
        flex_type.Description = "Amino change info in HGVS terms"

        multi_entry_type_de = cx.MultilingualEntryType(Lang='de', Value='aa_change')
        multi_entry_type_en = cx.MultilingualEntryType(Lang='en', Value='aa_change')
        multi_entry_type_de_desc = cx.MultilingualEntryType(Lang='de', Value='aa_change')
        multi_entry_type_en_desc = cx.MultilingualEntryType(Lang='en', Value='aa_change')

        flex_type.NameMultilingualEntries = [multi_entry_type_de, multi_entry_type_en]
        flex_type.DescMultilingualEntries = [multi_entry_type_de_desc, multi_entry_type_en_desc]

        flexible_value_ci.append(flex_type)
    
    def _addtranscript(self, flexible_value_ci):
        """Add the transcript ID"""
        flex_type = cx.FlexibleStringType()
        flex_type.Code = "{}transcript".format(cxu.CV_PREFIX)
        flex_type.Name = "Transcript ID"
        flex_type.ShortName = "Transcript ID"
        flex_type.Description = "External db transcript identifier"

        multi_entry_type_de = cx.MultilingualEntryType(Lang='de', Value='transcript')
        multi_entry_type_en = cx.MultilingualEntryType(Lang='en', Value='transcript')
        multi_entry_type_de_desc = cx.MultilingualEntryType(Lang='de', Value='transcript')
        multi_entry_type_en_desc = cx.MultilingualEntryType(Lang='en', Value='transcript')

        flex_type.NameMultilingualEntries = [multi_entry_type_de, multi_entry_type_en]
        flex_type.DescMultilingualEntries = [multi_entry_type_de_desc, multi_entry_type_en_desc]

        flexible_value_ci.append(flex_type)
    
    def _addfunctionalclass(self, flexible_value_ci):
        """Add the functional class of the variant"""
        flex_type = cx.FlexibleStringType()
        flex_type.Code = "{}functional_class".format(cxu.CV_PREFIX)
        flex_type.Name = "Functional class"
        flex_type.ShortName = "Functional class"
        flex_type.Description = "The functional class of the variant"

        multi_entry_type_de = cx.MultilingualEntryType(Lang='de', Value='functional_class')
        multi_entry_type_en = cx.MultilingualEntryType(Lang='en', Value='functional_class')
        multi_entry_type_de_desc = cx.MultilingualEntryType(Lang='de', Value='functional_class')
        multi_entry_type_en_desc = cx.MultilingualEntryType(Lang='en', Value='functional_class')

        flex_type.NameMultilingualEntries = [multi_entry_type_de, multi_entry_type_en]
        flex_type.DescMultilingualEntries = [multi_entry_type_de_desc, multi_entry_type_en_desc]

        flexible_value_ci.append(flex_type)

    def _addeffects(self, flexible_value_ci):
        """Adds the effects of the somatic SNVs"""
        flex_enum_value = cx.FlexibleEnumerationType()
        flex_enum_value.Code = "{}effect".format(cxu.CV_PREFIX)
        flex_enum_value.Name = "Effect of SNV"
        flex_enum_value.ShortName = "Effect"
        flex_enum_value.ChoiseType = "SELECTONE"
        flex_enum_value.Description = "Enumeration of different effects resulting from the variant"

        multi_entry_type_de = cx.MultilingualEntryType(Lang='de', Value='effect')
        multi_entry_type_en = cx.MultilingualEntryType(Lang='en', Value='effect')
        multi_entry_type_de_desc = cx.MultilingualEntryType(Lang='de', Value='effect')
        multi_entry_type_en_desc = cx.MultilingualEntryType(Lang='en', Value='effect')

        flex_enum_value.NameMultilingualEntries = [multi_entry_type_de, multi_entry_type_en]
        flex_enum_value.DescMultilingualEntries = [multi_entry_type_de_desc, multi_entry_type_en_desc]

        flex_enum_value.UsageEntryTypeRef = ["{}{}".format(cxu.CV_PREFIX, effect) for effect in cxu.CV_EFFECT_SSNV]
        flexible_value_ci.append(flex_enum_value)

    def _addchromosomes(self, flexible_value_ci):
        """Adds the chromosome enumerations"""
        flex_enum_value = cx.FlexibleEnumerationType()
        flex_enum_value.Code = "{}chr".format(cxu.CV_PREFIX)
        flex_enum_value.Name = "Chromosome Enumeration"
        flex_enum_value.ShortName = "chr"
        flex_enum_value.ChoiseType = "SELECTONE"
        flex_enum_value.Description = "Chromosome enumeration of the human chromosomes."
        
        multi_entry_type_de = cx.MultilingualEntryType(Lang='de', Value='Chromosome')
        multi_entry_type_en = cx.MultilingualEntryType(Lang='en', Value='Chromosome')

        multi_entry_type_de_desc = cx.MultilingualEntryType(Lang='de', Value='Chromosome')
        multi_entry_type_en_desc = cx.MultilingualEntryType(Lang='en', Value='Chromosome')

        flex_enum_value.NameMultilingualEntries = [multi_entry_type_de, multi_entry_type_en]
        flex_enum_value.DescMultilingualEntries = [multi_entry_type_de_desc, multi_entry_type_en_desc]

        flex_enum_value.UsageEntryTypeRef = ["{}{}{}".format(cxu.CV_PREFIX,'chr',index) for index in cxu.CV_CHROMOSOMES]
        flexible_value_ci.append(flex_enum_value)

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
