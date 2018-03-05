import os
import csv
import pandas
import argparse
import random
import collections
import itertools
import datetime
import numpy


from pgtools import toolbox
DATA_BASEPATH = toolbox.home_path('orthology/')
MODENCODE_TABLE_FNAME = os.path.join(DATA_BASEPATH, 'modencode/modencode.common.orth.txt')


def load_modencode(table_fname=MODENCODE_TABLE_FNAME, species_list=None, one_to_one=True):
    """
    Given the filename of the modEncode otrhology table, return a table
    of only the species in :species_list:, with gene names cleaned up.
    
    Still don't know what the last two columns a
    """
    modencode_orth = pandas.read_csv(table_fname, sep='\t', index_col=0,
                                 names=['species_a', 'species_b', 'gene_a', 'gene_b', 'count_a', 'count_b'])
    filtered_table = modencode_orth.copy()
  
    if species_list:
        filtered_table=filtered_table.loc[numpy.in1d(modencode_orth.species_a, species_list) & numpy.in1d(modencode_orth.species_b, species_list)]
 
    if one_to_one:
        filtered_table = filtered_table.loc[(filtered_table.count_a == 1) & (filtered_table.count_b == 1)]
        
    filtered_table.gene_a = [gene.split('_')[-1] for gene in filtered_table.gene_a]
    filtered_table.gene_b = [gene.split('_')[-1] for gene in filtered_table.gene_b]

    return filtered_table


class ModencodeTranslator():
    def _print(self, text):
        if self.verbose:
            print(text)
    
    def __init__(self, table_fname=MODENCODE_TABLE_FNAME, species_list=('mouse', 'human'), one_to_one=True, verbose=True):
        """
        Translates gene common names (only (for now)) between model organism species using data from the 
        modEncode project (http://compbio.mit.edu/modencode/orthologs/)
        
        Pre-filter using :species_list: for a slight performance gain.
        
        Currently doesn't handle one-to-many assignments properly, need to adapt code from Translator class.
        """
        self.verbose = verbose
        start_time = datetime.datetime.now()
        self._print('Populating orthology data for {} from {} ...'.format(', '.join(species_list), table_fname))
        if one_to_one:
            self._print('\tUsing one-to-one orthologs only')
                        
        modencode_table = load_modencode(MODENCODE_TABLE_FNAME, species_list=species_list, one_to_one=one_to_one)
        self._translation=collections.defaultdict(lambda: collections.defaultdict(lambda: {}))
        
        for species_a, outer_group in modencode_table.groupby('species_a'):
            for species_b, inner_group in outer_group.groupby('species_b'):
                
                self._translation[species_a][species_b] = {gene_a:gene_b for gene_a, gene_b in zip(modencode_table.gene_a, modencode_table.gene_b)}
                self._translation[species_b][species_a] = {gene_b:gene_a for gene_a, gene_b in zip(modencode_table.gene_a, modencode_table.gene_b)}

        self._print('Done in {}'.format(datetime.datetime.now() - start_time))
        
    def translate(self, gene_list, source_species, destination_species):
        self._print('Translating {} gene names from {} to {}'.format(len(gene_list), source_species, destination_species))
        assert source_species in self._translation, 'Source species {} not found!'.format(source_species)
        assert destination_species in self._translation[source_species], 'Destination species {} not found!'.format(destination_species)
        translated_list = []
        
        for gene in gene_list:
            if gene in self._translation[source_species][destination_species]:
                translated_list.append(self._translation[source_species][destination_species][gene])
            else:
                translated_list.append('')
        return translated_list


class Translator(object):
    """
    This class aims to provide a single object that knows how to translate
    various types of gene identifiers both between datasets and across species.
    """
    SPECIES_LINEAN = {'human':'Homo sapiens', 'mouse': 'Mus musculus'}
    SINGLE_SPECIES_FIELDNAMES = {'ensembl':['Ensembl Gene ID'],
                                'refseq':['RefSeq mRNA [e.g. NM_001195597]',    'RefSeq ncRNA [e.g. NR_002834]'],
                                'gene_name':['Associated Gene Name']}
    ORTHOLOGY_BIOMART_FIELDNAMES = {'source_ensembl':'Ensembl Gene ID',
                                    'destination_ensembl':'{} Ensembl Gene ID',
                                    'confidence_score':'{} orthology confidence [0 low, 1 high]'}
    VALID_ORTHOLOGY_SOURCES = ('compara', 'modencode', 'biomart')
    VALID_MULTI = ('none', 'all', 'first', 'last', 'random')
    VALID_FORMATS = set(['ensembl', 'refseq', 'gene_name'])

    def __init__(self, species_list=('human', 'mouse'), data_basepath=DATA_BASEPATH, ensembl_release=84, orthology_source='compara', species_style='new', verbose=True):
        self.verbose=verbose
        self.data_basepath = data_basepath
        self.ensembl_basepath = os.path.join(self.data_basepath, 'ensembl_{}'.format(ensembl_release))

        self.species_translations = {}
        for species in species_list:
            self._populate_single_species(species, species_style=species_style)

        if len(species_list) > 1:
            self.orthology = collections.defaultdict(lambda: collections.defaultdict(lambda: {}))
            self._populate_orthology(species_list=species_list, orthology_source=orthology_source)   


    def _print(self, text):
        if self.verbose:
            print(text)

    def _populate_single_species_twofiles(self, species):
        # ToDo: auto-generate files from SQL query if not present
        print('Populating info for {}'.format(species))

        self.species_translations[species] = {'ensembl': {'refseq':collections.defaultdict(lambda: set([])), 'gene_name':collections.defaultdict(lambda: set([]))},
                                              'refseq': {'ensembl':collections.defaultdict(lambda: set([]))},
                                              'gene_name': {'ensembl':collections.defaultdict(lambda: set([]))}}

        refseq_fname = os.path.join(self.ensembl_basepath, '{}_ensembl_refseq_mrna.tsv'.format(species))
        print(('\tPopulating RefSeq transcript IDs from {} ...'.format(refseq_fname)))
        e_to_r = self.species_translations[species]['ensembl']['refseq']
        r_to_e = self.species_translations[species]['refseq']['ensembl']
        with open(refseq_fname, 'rt') as refseq_file:
            header = refseq_file.readline()
            for line in refseq_file:
                ensembl_id, refseq_id = line.strip().split('\t')
                e_to_r[ensembl_id].add(refseq_id)
                r_to_e[refseq_id].add(ensembl_id)

        gene_name_fname = os.path.join(self.ensembl_basepath, '{}_ensembl_to_gene_name.tsv'.format(species))
        print('\tPopulating gene names from {} ...'.format(gene_name_fname))
        e_to_gn = self.species_translations[species]['ensembl']['gene_name']
        gn_to_e = self.species_translations[species]['gene_name']['ensembl']
        with open(gene_name_fname, 'rt') as gene_name_file:
            header = gene_name_file.readline()
            for line in gene_name_file:
                ensembl_id, gene_name = line.strip().split('\t')
                e_to_gn[ensembl_id].add(gene_name)
                gn_to_e[gene_name].add(ensembl_id)

        # Make caseless dictionaries
        for source_format in self.species_translations[species]:
            for dest_format in self.species_translations[species][source_format]:
                self.species_translations[species][source_format][dest_format] = toolbox.CaselessDict(self.species_translations[species][source_format][dest_format])

    def _populate_single_species(self, species, make_caseless=False, species_style='new'):
        if species_style=='new':
            self._populate_single_species_onefile(species, make_caseless)
        else:
            self._populate_single_species_twofiles(species)

    def _populate_single_species_onefile(self, species, make_caseless):
        # ToDo: auto-generate files from SQL query if not present
        print('Populating info for {}'.format(species))

        self.species_translations[species] = {'ensembl': {'refseq':collections.defaultdict(lambda: set([])), 'gene_name':collections.defaultdict(lambda: set([]))},
                                              'refseq': {'ensembl':collections.defaultdict(lambda: set([])), 'gene_name':collections.defaultdict(lambda: set([]))},
                                              'gene_name': {'refseq':collections.defaultdict(lambda: set([])), 'ensembl':collections.defaultdict(lambda: set([]))}}


        data_fname = os.path.join(self.ensembl_basepath, '{}_genes_biomart.tsv'.format(species))

        print('\tPopulating info from {} ...'.format(data_fname))
        with open(data_fname, 'rt') as data_file:
            reader=csv.DictReader(data_file, dialect=csv.excel_tab)
            #header = data_file.readline()
            for line in reader:
                for source_type, dest_type in itertools.permutations(self.SINGLE_SPECIES_FIELDNAMES, 2):
                    #print source_type, dest_type
                    for source_field, dest_field in itertools.product(self.SINGLE_SPECIES_FIELDNAMES[source_type], self.SINGLE_SPECIES_FIELDNAMES[dest_type]):
                     #   print source_field, dest_field
                        if line[source_field] and line[dest_field]:
                            self.species_translations[species][source_type][dest_type][line[source_field]].add(line[dest_field])
                    
        if make_caseless:
            # Make caseless dictionaries
            for source_format in self.species_translations[species]:
                for dest_format in self.species_translations[species][source_format]:
                    self.species_translations[species][source_format][dest_format] = toolbox.CaselessDict(self.species_translations[species][source_format][dest_format])
        print('\tDone.')
        
    def _populate_orthology(self, species_list, orthology_source='biomart',  minimum_confidence=0):
        toolbox.check_params('orthology_source', orthology_source, self.VALID_ORTHOLOGY_SOURCES)
        print('Populating interspecies homologs for {} using {}'.format(', '.join(species_list), orthology_source))
        if orthology_source in ('biomart', 'compara'):
            for species_pair in itertools.permutations(species_list, 2):
                self._populate_orthology_one_species(*species_pair, orthology_source=orthology_source)
                
        elif orthology_source == 'modencode':            
            self._populate_orthology_modencode(species_list)
                    
    def _populate_orthology_modencode(self, species_list, one_to_one=True):
        start_time = datetime.datetime.now()
        modencode_table_fname=os.path.join(DATA_BASEPATH, 'modencode/modencode.orth.txt')
        #self._print('Populating orthology data for {} from {} ...'.format(', '.join(species_list), modencode_table_fname))            
        
        if one_to_one:
            self._print('\tUsing one-to-one orthologs only')
                        
        modencode_table = load_modencode(modencode_table_fname, species_list=species_list, one_to_one=one_to_one)
        #self.orthology=collections.defaultdict(lambda: collections.defaultdict(lambda: {}))
        
        for species_a, outer_group in modencode_table.groupby('species_a'):
            for species_b, inner_group in outer_group.groupby('species_b'):
                
                self.orthology[species_a][species_b] = {gene_a:gene_b for gene_a, gene_b in zip(modencode_table.gene_a, modencode_table.gene_b)}
                self.orthology[species_b][species_a] = {gene_b:gene_a for gene_a, gene_b in zip(modencode_table.gene_a, modencode_table.gene_b)}
        self._print('Done in {}'.format(datetime.datetime.now() - start_time))

    
    def _populate_orthology_one_species(self, source_species, destination_species, orthology_source='biomart',  minimum_confidence=0):
        # ToDo: extend to one2many
        # ToDo: load all source-destination pairs in same operation (more efficient)
        #assert orthology_source in self.VALID_ORTHOLOGY_SOURCES, 'Invalid orthology source {}. Valid options are: {}'.format(orthology_source, ', '.join(self.VALID_ORTHOLOGY_SOURCES))

        if source_species not in self.orthology:
            self.orthology[source_species] = {}

        if orthology_source == 'compara':
            orthology_fname = os.path.join(self.ensembl_basepath,'{}_{}_compara_one2one.tsv'.format(*sorted((source_species, destination_species))))
            orthology_data = pandas.read_csv(orthology_fname, sep='\t')

            source_col_name = '_'.join(self.SPECIES_LINEAN[source_species].lower().split(' '))
            dest_col_name = '_'.join(self.SPECIES_LINEAN[destination_species].lower().split(' '))

            if orthology_data['gene1_organism'].iloc[0] == source_col_name and orthology_data['gene2_organism'].iloc[0] ==  dest_col_name:
                source_num, destination_num = 1, 2
            elif orthology_data['gene2_organism'].iloc[0] == source_col_name and orthology_data['gene1_organism'].iloc[0] ==  dest_col_name:
                source_num, destination_num = 2, 1
            else:
                raise Exception('This does not appear to be a valid {} orthology file'.format(orthology_source))

            self.orthology[source_species][destination_species] = dict([(ensembl_id1, set([ensembl_id2])) for ensembl_id1, ensembl_id2 in zip(orthology_data.loc[:, ('gene{}_id'.format(source_num))], orthology_data.loc[:, ('gene{}_id'.format(destination_num))])])
            
        elif orthology_source == 'biomart':
            orthology_fname = os.path.join(self.ensembl_basepath,'{}_to_{}_biomart.tsv'.format(source_species, destination_species))
            orthology_data = pandas.read_csv(orthology_fname, sep='\t')
            
            # lowercase the column names to simplify matching:
            orthology_data.columns = [col.lower() for col in orthology_data.columns]

            source_col_name = self.ORTHOLOGY_BIOMART_FIELDNAMES['source_ensembl'].lower()
            destination_col_name = self.ORTHOLOGY_BIOMART_FIELDNAMES['destination_ensembl'].format(destination_species).lower()
            confidence_col_name = self.ORTHOLOGY_BIOMART_FIELDNAMES['confidence_score'].format(destination_species).lower()
            
            #print(orthology_data.columns)
            #print(source_col_name, destination_col_name,confidence_col_name)
            
            self.orthology[source_species][destination_species] = {source_ensembl_id:set([destination_ensembl_id]) for source_ensembl_id, destination_ensembl_id, confidence in zip(orthology_data[source_col_name], orthology_data[destination_col_name], orthology_data[confidence_col_name]) if confidence >= minimum_confidence}
            #self.orthology[source_species][destination_species] = dict([(ensembl_id1, set([ensembl_id2])) for ensembl_id1, ensembl_id2 in zip(orthology_data.loc[:, ('gene{}_id'.format(source_num))], orthology_data.loc[:, ('gene{}_id'.format(destination_num))])])
            
    def _robust_translate(self, identifier_list, translation_dict, multi='none'):
        assert multi in self.VALID_MULTI, 'Invalid value {} for multi-mapping handling. Valid options are: {}'.format(multi, ', '.join(VALID_MULTI))
        translated_list = []
        for identifier in identifier_list:
            if identifier in translation_dict:
                destination_genes = list(translation_dict[identifier])
                if len(destination_genes) > 1:
                    if multi == 'none':
                        # warn
                        print('Multiple translations for {}: {}'.format(identifier, ', '.join(sorted(translation_dict[identifier]))))
                        translated_list.append('')
                    elif multi == 'all':
                        translated_list += destination_genes
                    elif multi == 'first':
                        translated_list.append(destination_genes[0])
                    elif multi == 'last':
                        translated_list.append(destination_genes[-1])
                    elif multi == 'random':
                        translated_list.append(random.choice(destination_genes))
                else:
                    translated_list.append(destination_genes[0])
            else:
                translated_list.append('')
        return translated_list
        
    def all_ids(self, species, id_format):
        """
        Returns a list of all known identifiers for the given species in the given format.
        """
        pass
    
    def translate(self, identifier_list, source_species, source_format, destination_format=None, destination_species=None, use_source_if_dest_not_found=False, multi='none'):
        
        
        destination_ids = self.translate_onestep(identifier_list=identifier_list,
                                         source_species=source_species,
                                         source_format=source_format,
                                         destination_format=destination_format,
                                         destination_species=destination_species,
                                         multi=multi)
                                         
        if use_source_if_dest_not_found:
            for i in range(len(identifier_list)):  
                if not destination_ids[i]:
                    #print(identifier_list[i])
                    destination_ids[i] = identifier_list[i]
        
        return destination_ids

    def translate_twostep(self, identifier_list, source_species, source_format, destination_format=None, destination_species=None, multi=False):
        assert destination_format or destination_species
        assert source_format in self.VALID_FORMATS, 'Invalid source format {}. Valid formats are: {}'.format(source_format, ', '.join(self.VALID_FORMATS))
        assert destination_format in self.VALID_FORMATS, 'Invalid destination format {}. Valid formats are: {}'.format(destination_format, ', '.join(self.VALID_FORMATS))
        
        if not destination_species:
            destination_species = source_species
        if not destination_format:
            destination_format = source_format

        # first get to ensembl ids in the source species
        if source_format != 'ensembl':
            print('\tTranslating from {} {} to {} Ensembl IDs'.format(source_species, source_format, source_species))
            source_species_ensembl_ids = self._robust_translate(identifier_list, self.species_translations[source_species][source_format]['ensembl'])
        else:
            source_species_ensembl_ids = identifier_list

        # now move species if necessary
        if destination_species != source_species:
            print('\tTranslating Ensembl IDs from {} to {}'.format(source_species, destination_species))
            destination_species_ensembl_ids = self._robust_translate(source_species_ensembl_ids, self.orthology[source_species][destination_species])
        else:
            destination_species_ensembl_ids = source_species_ensembl_ids

        # now change formats in the destination species
        if destination_format != 'ensembl':
            print('\tTranslating from {} Ensembl IDs to {} {} '.format(destination_species, destination_species, destination_format))
            destination_ids = self._robust_translate(destination_species_ensembl_ids, self.species_translations[destination_species]['ensembl'][destination_format])
        else:
            destination_ids = destination_species_ensembl_ids

        return destination_ids
        
        
    def translate_onestep(self, identifier_list, source_species, source_format, destination_format=None, destination_species=None, multi='none'):
        assert destination_format or destination_species
        assert source_format in self.VALID_FORMATS, 'Invalid source format {}. Valid formats are: {}'.format(source_format, ', '.join(self.VALID_FORMATS))
        assert destination_format in self.VALID_FORMATS, 'Invalid destination format {}. Valid formats are: {}'.format(destination_format, ', '.join(self.VALID_FORMATS))
 
        if not destination_species:
            destination_species = source_species
        if not destination_format:
            destination_format = source_format

        print('Converting {} gene identifiers from {} {} to {} {} ...'.format(len(identifier_list), source_species, source_format, destination_species, destination_format))

        if destination_species == source_species:
            print('Same species: {}'.format(destination_species))
            return self._robust_translate(identifier_list, self.species_translations[source_species][source_format][destination_format], multi=multi)
        
        else:
            # first get to ensembl ids in the source species
            if source_format != 'ensembl':
                print('\tTranslating from {} {} to {} Ensembl IDs'.format(source_species, source_format, source_species))
                source_species_ensembl_ids = self._robust_translate(identifier_list, self.species_translations[source_species][source_format]['ensembl'], multi=multi)
            else:
                source_species_ensembl_ids = identifier_list
            #print source_species_ensembl_ids
            print('\tTranslating Ensembl IDs from {} to {}'.format(source_species, destination_species))
            destination_species_ensembl_ids = self._robust_translate(source_species_ensembl_ids, self.orthology[source_species][destination_species], multi=multi)
            #print destination_species_ensembl_ids
            # now change formats in the destination species
            if destination_format != 'ensembl':
                print('\tTranslating from {} Ensembl IDs to {} {} '.format(destination_species, destination_species, destination_format))
                destination_ids = self._robust_translate(destination_species_ensembl_ids, self.species_translations[destination_species]['ensembl'][destination_format])
            else:
                destination_ids = destination_species_ensembl_ids
            #print destination_ids
        return destination_ids

def main():
    arg_parser = argparse.ArgumentParser('Name translator')
    arg_parser.add_argument('input_file', help='The name of a file containing a list of gene identifiers to be translated')
    arg_parser.add_argument('source_species')
    arg_parser.add_argument('source_format')
    arg_parser.add_argument('destination_species')
    arg_parser.add_argument('destination_format')
    arg_parser.add_argument('multi', default='none', help='How to handle one_to_many mappings. Options are: none, all, first, last, random')

    args = arg_parser.parse_args()

    translator = Translator()

    with open(args.input_file, 'rt') as in_file:
        input_ids = [line.strip() for line in in_file.readlines()]
    print('Loaded {} gene identifiers from {}'.format(len(input_ids), args.input_file))

    output_ids = translator.translate(input_ids, source_species=args.source_species,
                                      source_format=args.source_format,
                                      destination_format=args.destination_format,
                                      destination_species=args.destination_species,
                                      use_source_if_dest_not_found=True,
                                      multi=args.multi)

    output_fname = args.input_file + '_translated'
    print('Writing {} translated identifiers to {}'.format(len(output_ids), output_fname))
    with open(output_fname, 'wt') as out_file:
        for identifier in output_ids:
            out_file.write(identifier + '\n')

if __name__ == '__main__':
    main()
