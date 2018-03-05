import datetime
import numpy
import pandas
import goatools
import goatools.associations
import statsmodels.sandbox.stats.multicomp
import openpyxl

from pgtools import toolbox


GO_ASSOCIATION_FIELD_DESCRIPTION_TEXT = """Column	Content	Required?	Cardinality	Example
1	DB	required	1	UniProtKB
2	DB Object ID	required	1	P12345
3	DB Object Symbol	required	1	PHO3
4	Qualifier	optional	0 or greater	NOT
5	GO ID	required	1	GO:0003993
6	DB:Reference (|DB:Reference)	required	1 or greater	PMID:2676709
7	Evidence Code	required	1	IMP
8	With (or) From	optional	0 or greater	GO:0000346
9	Aspect	required	1	F
10	DB Object Name	optional	0 or 1	Toll-like receptor 4
11	DB Object Synonym (|Synonym)	optional	0 or greater	hToll|Tollbooth
12	DB Object Type	required	1	protein
13	Taxon(|taxon)	required	1 or 2	taxon:9606
14	Date	required	1	20090118
15	Assigned By	required	1	SGD
16	Annotation Extension	optional	0 or greater	part_of(CL:0000576)
17	Gene Product Form ID	optional	0 or 1	UniProtKB:P12345-2"""
fd=numpy.array([numpy.array(line.split('\t')) for line in GO_ASSOCIATION_FIELD_DESCRIPTION_TEXT.split('\n')])
GO_ASSOCIATION_FIELD_DESCRIPTION = pandas.DataFrame(data=fd[1:], columns=fd[0])

OBO_FILENAME = '/home/dskola/GO/go.obo'
HUMAN_GO_ASSOCIATION_FILENAME = '/home/dskola/GO/human_goa_associations.txt'
MOUSE_GO_ASSOCIATION_FILENAME = '/home/dskola/GO/mouse_goa_associations.txt'

SPECIES_INFO = {'mouse': {'go_association_filename': MOUSE_GO_ASSOCIATION_FILENAME},
                'human': {'go_association_filename': HUMAN_GO_ASSOCIATION_FILENAME}}


def load_go_associations(go_assoc_filename):
    return pandas.read_csv(go_assoc_filename, names=GO_ASSOCIATION_FIELD_DESCRIPTION['Content'], sep='\t', comment='!', low_memory=False)


def genes_by_go_term(go_df, go_term, output_filename):
    """
    Given a pandas DataFrame containing GO term - gene associations in the
    format of the downloadable files from the Gene Ontology consortium,
    write out a list of genes associated with the specified GO term.
    """
    gene_list = sorted(set(go_df[go_df['GO ID'] == go_term]['DB Object Symbol']))
    print(('Writing {} genes matching {} to {}'.format(len(gene_list), go_term, output_filename)))
    with open(output_filename, 'wt') as out_file:
        for gene in gene_list:
            out_file.write(gene + '\n')


def export_associations_for_goatools(go_df, output_filename):
    """
    Given a pandas DataFrame containing GO term - gene associations in the
    format of the downloadable files from the Gene Ontology consortium,
    write a text file containing each gene on a line, followed by a semi-colon
    separated list of GO terms associated with that gene. This is the format
    used by the goatools module.
    """
    with open(output_filename, 'wt') as out_file:
        for gene, group in go_df.groupby(['DB Object Symbol']):
            out_file.write('{}\t{}\n'.format(gene, ';'.join(group['GO ID'])))

            
class GOMaster(object):
    def __init__(self, obo_filename=OBO_FILENAME, species='human'):
        """
        Populates itself with the GO DAG and child-term-gene associations, then
        propagates those and allows querying term associations by either gene or go term.
        """
        self._go_dag = goatools.obo_parser.GODag(obo_filename)
        self._gene_assoc = goatools.associations.read_associations(SPECIES_INFO[species]['go_association_filename'])
        print('Propagating assocatiations...')
        self._go_dag.update_association(self._gene_assoc)
        print('Inverting associations...')
        self._go_assoc = toolbox.invert_dict(self._gene_assoc, multi_value=True)
       
    def genes_by_go_term(self, go_term):
        if go_term in self._go_assoc:
            gene_list = sorted(self._go_assoc[go_term])
            print(('Found {} genes associated with {}'.format(len(gene_list), go_term)))
            return gene_list
        else:
            print(('GO term {} not found in GO associations'.format(go_term)))
         
    def go_terms_by_gene(self, gene):
        if gene in self._gene_assoc:
            term_list = sorted(self._gene_assoc[gene])
            print(('Found {} terms associated with {}'.format(len(term_list), gene)))
            return term_list
        else:
            print(('Gene {} not found in GO associations'.format(gene)))


class GoEnrichmentTester(object):
    MULTIPLE_TESTING_METHODS = {'none': 'p_uncorrected',
                                'bonferroni':'p_bonferroni',
                                'sidak':'p_sidak',
                                'holm':'p_holm',
                                'bh':'p_bh',
                                'fdr':'p_fdr'}
    
    def __init__(self, species, obo_filename = OBO_FILENAME):
        """
        Convenience class that wraps goatools to compute and format GO term
        enrichment results.
        """
        start_time = datetime.datetime.now()
        print('Initializing gene enrichment tester for species: {}'.format(species))
        assert species in SPECIES_INFO, 'Unknown species {}. Acceptable choices: {}'.format(species, ', '.join(sorted(SPECIES_INFO.keys())))
        
        print('Loading GO DAG from {}...'.format(obo_filename))
        self.go_dag = goatools.obo_parser.GODag(obo_filename)
        print('Loading GO term to gene associations from {}...'.format(SPECIES_INFO[species]['go_association_filename']))
        self.go_assoc = goatools.associations.read_associations(SPECIES_INFO[species]['go_association_filename'])
        print('\tDone in {}'.format(datetime.datetime.now() - start_time))

    def _convert_records_to_df(self, list_of_records, use_pseudocount=True):
        column_dict = {'log2_enrichment':numpy.zeros(len(list_of_records), dtype=float)}
        for record_idx, record in enumerate(list_of_records):
            for field, value in zip(record.get_prtflds_default(), record.get_field_values(record.get_prtflds_default(), rpt_fmt=False)):
                
                if type(value) == type('str'):
                    dtype= numpy.object
                else:
                    dtype = type(value)
                
                if field not in column_dict:
                    column_dict[field] = numpy.zeros(len(list_of_records), dtype=dtype)
                    
                column_dict[field][record_idx] = value
                
            pop_ratio_tuple = column_dict['ratio_in_pop'][record_idx]
            pop_ratio = (pop_ratio_tuple[0] + int(use_pseudocount)) / float(pop_ratio_tuple[1] + int(use_pseudocount))
            study_ratio_tuple = column_dict['ratio_in_study'][record_idx]
            study_ratio = (study_ratio_tuple[0] + int(use_pseudocount)) / float(study_ratio_tuple[1]+ int(use_pseudocount))
            
            if pop_ratio != 0:
                column_dict['log2_enrichment'][record_idx] = numpy.log2(study_ratio / pop_ratio)
            else:
                column_dict['log2_enrichment'][record_idx] = float('Inf')
                
        column_dict['p_bh'] = statsmodels.sandbox.stats.multicomp.fdrcorrection0(column_dict['p_uncorrected'])[1]
        
        return pandas.DataFrame(data=column_dict)
        
    def compute_enrichment(self, study_genes, population_genes, alpha=0.05, threshold_on='bonferroni', use_pseudocount=True):
        """
        Computes the enrichment of GO terms in `study_genes` compared to `population_genes`
        """
        assert threshold_on in self.MULTIPLE_TESTING_METHODS, 'Invalid multiple testing method for thresholding: {}. Valid options: {}'.format(threshold_on, ', '.join(list(self.MULTIPLE_TESTING_METHODS.keys())))
        
        start_time = datetime.datetime.now()
        print('Computing GO term enrichment for {} study genes and {} population genes'.format(len(study_genes), len(population_genes)))
        
        this_study = goatools.GOEnrichmentStudy(pop=population_genes,
                                assoc=self.go_assoc,
                                obo_dag=self.go_dag,
                                propagate_counts=True,
                                #study=study_genes,
                                methods=['bonferroni', 'holm', 'sidak'],
                                alpha=0.99)
        
        results=this_study.run_study(study_genes)
                           
                                
        result_df = self._convert_records_to_df(results, use_pseudocount=use_pseudocount)
        result_df = result_df[result_df[self.MULTIPLE_TESTING_METHODS[threshold_on]] <= alpha]
        
        print('\tDone in {}'.format(datetime.datetime.now() - start_time))
        
        return result_df
        

class MetascapeResult():
    def __init__(self, metascape_excel_fname, fdr=0.05, delog_q_vals=False):
        """
        Wrapper class for parsing MetaScape output Excel files. Currently just creates
        an attribute :go_term_summary_table:
        
        The openpyxl.WorkBook object for the result file is exposed in the attribute :workbook:
        """
        print('Loading MetaScape results from {}'.format(metascape_excel_fname))
        self.workbook = openpyxl.load_workbook(metascape_excel_fname)
        self._create_go_term_summary_table(fdr, delog_q_vals)
        
    def _create_go_term_summary_table(self, fdr, delog_q_vals=True):
        print('Creating GO term summary table using an FDR of {}'.format(fdr))
        df = pandas.DataFrame(self.workbook['Enrichment'].values)
        df.columns = df.iloc[0,:]
        df = df.iloc[1:,:]
        df.index = df.iloc[:,0]
        df = df.iloc[:,1:]
        df = df.loc[[name.endswith('_Summary') for name in df.index]]
        df.index = df['Term']
        df.iloc[:,3] = numpy.array(df.iloc[:,3]).astype(float)
        df = df.loc[:,['Category', 'Term', 'Description', 'Log(q-value)']]
        
        if fdr:
            df = df.loc[df['Log(q-value)'] <= numpy.log10(fdr)]
            
        if delog_q_vals:
            df['Log(q-value)'] = 10**df['Log(q-value)']
            df.rename(columns={'Log(q-value)':'q-value'}, inplace=True)
        df.iloc[:,3] = numpy.array(df.iloc[:,3]).astype(float)

        self.go_term_summary_table = df