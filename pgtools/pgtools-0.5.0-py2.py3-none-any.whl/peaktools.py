import os
import numpy
import pandas
import datetime
import subprocess
import matplotlib
import matplotlib.pyplot as plt
import matplotlib_venn
import seaborn

from pgtools import toolbox
import intervaltree
#import genomewrappers
from . import intervaloverlaps
from scipy.stats import gaussian_kde

NUM_CORES=8

TMP_DIR = '/tmp/dskola'

YESNO = {True:'yes',
         False:'no'}

GENOME_NAMES = {'mouse':'mm10', 'human':'hg38'}
BOWTIE2_PATH = 'bowtie2'
BOWTIE2_PARAMS = '--very-sensitive -N 1 -t'
BOWTIE2_INDICES = {'mouse': toolbox.home_path('model_data/reference_genomes/mm10/mm10'),
                   'human': toolbox.home_path('model_data/reference_genomes/hg38/hg38')}


# def infer_tag_path_from_replicate_info(df, replicate_name):
    # """
    # Given a dataframe <df> and a replicate name that corresponds to one of the rows in <df>,
    # return a path constructed from the info in the dataframe that points to the tag
    # directory of that replicate.
    # """
    # path = os.path.join(os.environ['HOME'],
                        # 'glass_data',
                        # {'human':'hg38', 'mouse':'mm10'}[df.loc[replicate_name, 'species']],
                        # 'Microglia',
                        # df.loc[replicate_name, 'assay_type'],
                        # (df.loc[replicate_name, 'assay_target'], '')[numpy.isnan(df.loc[replicate_name, 'assay_target'])],
                        # replicate_name
                       # )
    
    # if os.path.isdir(path):
        # return path
    # else:
        # print('Path {} not found'.format(path))
        # return None
    

# def display_replicates(replicate_dict, full_path=False):
    # for k in replicate_dict:
        # print(k)
        # print('\t{}'.format(replicate_dict[k]))
    # print()
    

# def get_full_rep_paths(replicate_dict, processed_tag_basepath, fasta_basepath):
    # rep_paths = []
    # for k in replicate_dict:
        # if replicate_dict[k].endswith('fastq.gz'):
            # rep_paths.append(os.path.join(fasta_basepath, replicate_dict[k]))
        # else:
            # subfolder = os.path.join(fasta_basepath, replicate_dict[k])
            # sub_reps = [os.path.join(subfolder, f) for f in os.listdir(subfolder) if f.endswith('fastq.gz')]
            # assert len(sub_reps) > 0
            # rep_paths += sub_reps
    # return rep_paths


def concat_reps(species, dataset_name, replicate_list, data_path_prefix=os.path.join(os.environ['HOME'], 'glass_data', 'archive')):
    """
    Given a species ('mouse' or 'human'), the name of a pooled dataset, and a list of gzipped FASTQ files in the path,
    will generate a pooled FASTQ file in HOME/remap. 
    """
    start_time = datetime.datetime.now() 
    destination_path = toolbox.home_path('remap/{}'.format(species))
    toolbox.establish_path(destination_path)
    print(data_path_prefix)
    cmd_line = ['zcat', ' '.join([os.path.join(data_path_prefix, replicate_path) for replicate_path in replicate_list]), '>', '{}/{}_{}_pooled.fastq'.format(destination_path, species, dataset_name)]
    print()
    print('Concatenating {} replicates'.format(len(replicate_list)))
    print()
    print(' '.join(cmd_line))
    print('Done in {}'.format(datetime.datetime.now() - start_time))
    output = subprocess.check_output(' '.join(cmd_line), shell=True, stderr=subprocess.STDOUT).decode()
    print(output)


def align_reads(species, dataset_name, num_cores=6):
    start_time = datetime.datetime.now() 
    print('Aligning {}, {} ...'.format(species, dataset_name))
    tag_folder = toolbox.home_path('{}/{}/{}_{}_pooled/'.format(species, dataset_name, species, dataset_name))
    remap_folder = toolbox.home_path('remap/{}/'.format(species))
    alignment_fname = os.path.join(remap_folder, '{}_{}_pooled.sam'.format(species, dataset_name))
    input_fname = os.path.join(remap_folder, '{}_{}_pooled.fastq'.format(species, dataset_name))
                                        
    toolbox.establish_path(tag_folder)
                                
    cmd_line = [BOWTIE2_PATH] + BOWTIE2_PARAMS.split(' ') + ['-p', str(num_cores),
                                                            '--met-file', os.path.join(tag_folder,'bowtie2.log'),
                                                              '-x', BOWTIE2_INDICES[species],
                                                             '-U', input_fname,
                                                             '-S', alignment_fname]
                                                             
    print(' '.join(cmd_line))
    output = subprocess.check_output(cmd_line, stderr=subprocess.STDOUT).decode()
    print(output)
    print('Done in {}'.format(datetime.datetime.now() - start_time))


def create_tag_folder(species, dataset_name):
    start_time = datetime.datetime.now() 
    alignment_fname = toolbox.home_path('remap/{}/{}_{}_pooled.sam'.format(species,  species, dataset_name))
    tag_folder = toolbox.home_path('{}/{}/{}_{}_pooled'.format(species, dataset_name, species, dataset_name))
    
    print('Making Tag folder {} ...'.format(tag_folder))
    cmd_line = ['makeTagDirectory',
                tag_folder,
               '-format',
               'sam',
               '-unique',
               '-genome',
               'mm10',
               '-checkGC',
               alignment_fname]
    print(' '.join(cmd_line))
    output = subprocess.check_output(cmd_line, stderr=subprocess.STDOUT)
    print(output)
    print()
    print('Making BEDgraph ...')
    cmd_line =['makeUCSCfile',
               tag_folder,
               '-o',
               'auto']
    output = subprocess.check_output(cmd_line, stderr=subprocess.STDOUT)
    print(output)
    print('Done in {}'.format(datetime.datetime.now() - start_time))


def peak_filename(species, dataset_name, style, size, min_dist, input_dataset_name='', region=False, nfr=False):
    """
    Returns the peak filename prefix corresponding to the specified parameters
    """
    return toolbox.home_path('{}/{}_{}_vsInput_{}_style_{}_region_{}_nfr_{}_size_{}_minDist_{}_peaks.tsv'.format(species,
                                                                                                                              species,
                                                                                                                              dataset_name,
                                                                                                                              YESNO[bool(input_dataset_name)],
                                                                                                                              style,
                                                                                                                              YESNO[region],
                                                                                                                              YESNO[nfr],
                                                                                                                              size,
                                                                                                                              min_dist))


                                                                                                                              
def call_peaks(chip_tag_folder, species, dataset_name, output_folder, style, size, min_dist, input_tag_folder='', region=False, nfr=False, tbp=0, genome_build='', other_params=''):
    start_time = datetime.datetime.now() 

    toolbox.establish_path(output_folder)                        
    output_fname = os.path.join(output_folder, '{}_{}_vsInput_{}_style_{}_region_{}_nfr_{}_size_{}_minDist_{}_peaks.tsv'.format(species, 
                                                                                                                                dataset_name,
                                                                                                                                YESNO[bool(input_tag_folder)],
                                                                                                                                style,
                                                                                                                                YESNO[region],
                                                                                                                                YESNO[nfr],
                                                                                                                                size,
                                                                                                                                min_dist))
                                                                                                      
    print('Calling peaks to {}'.format(output_fname))

    cmd_line=['findPeaks',
              chip_tag_folder,
              '-style', style,
              '-size', str(size),
              '-tbp', str(tbp),
              '-minDist', str(min_dist)] \
              + ([], ['-region'])[region] \
              + ([], ['-nfr'])[nfr] \
              + ([], ['-i', input_tag_folder])[bool(input_tag_folder)] \
              + other_params.split(' ') \
              + ['>', output_fname]
    print()
    print(' '.join(cmd_line))
    print()
    output = subprocess.check_output(' '.join(cmd_line), shell=True, stderr=subprocess.STDOUT).decode()
    print(output)
    print()
    if os.path.isfile(output_fname):
        print('Converting to BED ...')
        bed_fname = output_fname.split('.')[0] + '.bed'
        cmd_line = ['pos2bed.pl', output_fname, '>', bed_fname]
        print()
        print(' '.join(cmd_line))
        print()
        output = subprocess.check_output(' '.join(cmd_line), shell=True, stderr=subprocess.STDOUT).decode()
        print(output)
        print()
        print('Annotating peaks ...')
        print()
        annotated_fname = output_fname.split('.')[0] + '_annotated.tsv'
        if not genome_build:
            genome_build = GENOME_NAMES[species]
        cmd_line = ('annotatePeaks.pl', output_fname, genome_build, '>', annotated_fname)
        print(' '.join(cmd_line))
        print()
        output = subprocess.check_output(' '.join(cmd_line), shell=True, stderr=subprocess.STDOUT).decode()
        print(output)
        print('Done in {}'.format(datetime.datetime.now() - start_time))
        return annotated_fname                                                                                                                              
                                                                                                                              
                                                                                                                              
def call_peaks_pooled(species, dataset_name, style, size, min_dist, vs_input=True, region=False, nfr=False, tbp=0):
    start_time = datetime.datetime.now() 
    tag_folder = toolbox.home_path('{}/{}/{}_{}_pooled'.format(species, dataset_name, species, dataset_name))
    
    if vs_input:
        input_folder = toolbox.home_path('{}/input/{}_input_pooled'.format(species, species))
    else:
        input_folder = ''
    output_fname = peak_filename(species=species, dataset_name=dataset_name, style=style, size=size, min_dist=min_dist,
                                input_dataset_name=input_folder, region=region, nfr=region)
                                
    
    print('Calling peaks to {}'.format(output_fname))
    cmd_line=['findPeaks',
              tag_folder,
              '-style', style,
              '-size', str(size),
              '-tbp', str(tbp),
              '-minDist', str(min_dist)] \
              + ([], ['-region'])[region] \
              + ([], ['-nfr'])[nfr] \
              + ([], ['-i', input_folder])[bool(vs_input)] \
              + ['>', output_fname]
    print()
    print(' '.join(cmd_line))
    print()
    output = subprocess.check_output(' '.join(cmd_line), shell=True, stderr=subprocess.STDOUT).decode()
    print(output)
    print()
    if os.path.isfile(output_fname):
        print('Converting to BED ...')
        bed_fname = output_fname.split('.')[0] + '.bed'
        cmd_line = ['pos2bed.pl', output_fname, '>', bed_fname]
        print()
        print(' '.join(cmd_line))
        print()
        output = subprocess.check_output(' '.join(cmd_line), shell=True, stderr=subprocess.STDOUT).decode()
        print(output)
        print()
        print('Annotating peaks ...')
        print()
        annotated_fname = output_fname.split('.')[0] + '_annotated.tsv'
        cmd_line = ('annotatePeaks.pl', output_fname, GENOME_NAMES[species], '>', annotated_fname)
        print(' '.join(cmd_line))
        print()
        output = subprocess.check_output(' '.join(cmd_line), shell=True, stderr=subprocess.STDOUT).decode()
        print(output)
        print('Done in {}'.format(datetime.datetime.now() - start_time))
        return annotated_fname
    

def call_peaks_indv(peak_tag_folder, species, data_subtype, style, size, min_dist, vs_input=False, input_tag_folder='',region=False, nfr=False, tbp=0, output_path=''):
    
    start_time = datetime.datetime.now() 
    if vs_input and not input_tag_folder:
        input_tag_folder = toolbox.home_path('{}/input/{}_input_pooled'.format(species, species))
    assert os.path.isdir(peak_tag_folder)
    
    if input_tag_folder:
        assert os.path.isdir(input_tag_folder)
    
    if not output_path:
        output_path = toolbox.home_path('{}/{}'.format(species, data_subtype))
    toolbox.establish_path(output_path)
    
    output_fname = os.path.join(output_path, '{}_vsInput_{}_style_{}_region_{}_nfr_{}_size_{}_minDist_{}_peaks.tsv'.format(peak_tag_folder.split('/')[-1],
                                                                                                                              YESNO[vs_input],
                                                                                                                              style,
                                                                                                                              YESNO[region],
                                                                                                                              YESNO[nfr],
                                                                                                                              size,
                                                                                                                              min_dist))
    print('Calling peaks to {}'.format(output_fname))
    cmd_line=['findPeaks',
              peak_tag_folder,
              '-style', style,
              '-size', str(size),
              '-tbp', str(tbp),
              '-minDist', str(min_dist)] \
              + ([], ['-region'])[region] \
              + ([], ['-nfr'])[nfr] \
              + ([], ['-i', input_tag_folder])[vs_input] \
              + ['>', output_fname]
    print()
    print(' '.join(cmd_line))
    print()
    output = subprocess.check_output(' '.join(cmd_line), shell=True, stderr=subprocess.STDOUT).decode()
    print(output)
    print()
    print('Converting to BED ...')
    bed_fname = output_fname.split('.')[0] + '.bed'
    cmd_line = ['pos2bed.pl', output_fname, '>', bed_fname]
    print()
    print(' '.join(cmd_line))
    print()
    output = subprocess.check_output(' '.join(cmd_line), shell=True, stderr=subprocess.STDOUT).decode()
    print(output)
    print()
    print('Annotating peaks ...')
    print()
    annotated_fname = output_fname.split('.')[0] + '_annotated.tsv'
    cmd_line = ('annotatePeaks.pl', output_fname, GENOME_NAMES[species], '>', annotated_fname)
    print(' '.join(cmd_line))
    print()
    output = subprocess.check_output(' '.join(cmd_line), shell=True, stderr=subprocess.STDOUT).decode()
    print(output)
    print('Done in {}'.format(datetime.datetime.now() - start_time))
    return output_fname    


def filter_by_tss_distance(annotated_peak_filename, distance_threshold, distal_or_proximal=False):
    """
    Takes an annotated peak file as output by HOMER and filters peaks by their distance to the closest 
    transcription start site (TSS). If <keep_peaks_under_threshold> is False, peaks with a TSS distance
    greater than the threshold will be output, otherwise peaks under or equal to the threshold will be output.
    """
    start_time = datetime.datetime.now() 
    output_filename = annotated_peak_filename.split('.')[0] + '_{}_{}.tsv'.format(distal_or_proximal, distance_threshold)
    annotated_peaks = pandas.read_csv(annotated_peak_filename, sep='\t', comment='#', index_col=0)
    
    if distal_or_proximal == 'proximal':
        filtered_peaks = annotated_peaks[numpy.abs(annotated_peaks['Distance to TSS']) <= distance_threshold]
    elif distal_or_proximal == 'distal':
        filtered_peaks = annotated_peaks[numpy.abs(annotated_peaks['Distance to TSS']) > distance_threshold]
    else:
        raise ValueError('Invalid value for <distal_or_proximal>. Got {}'.format(distal_or_proximal))
        
    filtered_peaks.to_csv(output_filename, sep='\t')
    print('Done in {}'.format(datetime.datetime.now() - start_time))

    
def hard_max_peaks(peak_matrix, maximum_tag_count=2**8):
    filtered = peak_matrix.copy()
    for col in filtered.columns:
        filtered[col] = numpy.minimum(filtered[col], maximum_tag_count)
    return filtered

    
def threshold_by_tbp(peak_matrix, peak_annotations, max_tpb=1.0):
    filtered = peak_matrix.copy()
    peak_lengths = peak_annotations['End'] - peak_annotations['Start']
    for col in filtered.columns:
        tbp = peak_matrix[col] / peak_lengths
        filtered_tbp = numpy.minimum(max_tpb, tbp)
        filtered_tags = filtered_tbp * peak_lengths
        filtered[col] = filtered_tags
    return filtered


def merge_peaks(peak_files, output_fname):
    """
    Uses bedtools to merge (take the union of overlapping regions) a an iterable of BED files
    and output a single BED file.
    """
#     peak_files = [f for f in peak_files if os.path.isfile(os.path.join(source_folder, f))]
#     print(peak_files)

    cmd_line = ['cat'] + list(peak_files) + ['|', 'bedtools', 'sort', '|', 'bedtools', 'merge', '>', output_fname]
    
    print('Concatenating and merging {} to {} ...'.format(', '.join(peak_files), output_fname))
    try:
        output=subprocess.check_output(' '.join(cmd_line), stderr=subprocess.STDOUT, shell=True).decode()
    except subprocess.CalledProcessError as cpe:
        print(cpe)
    else:
        print(output)
    
    print('Done.')

    
def create_replicate_matrix(genome_build, tag_directories, merged_peak_file, output_fname, options=[]):
    """
    Given an iterable of tag directories and a BED file, count the reads in each
    region in the BED file and output the results in a matrix with peaks as rows and 
    tag directories as columns.
    """
    cmd_line = ['annotatePeaks.pl', merged_peak_file, genome_build, '-size', 'given'] + options + ['-d'] + list(tag_directories) + ['>', output_fname]
    print('Annotating peaks across {} replicates, outputting to {}'.format(len(tag_directories), output_fname))
    print()
    print(' '.join(cmd_line))
    try:
        output=subprocess.check_output(' '.join(cmd_line), stderr=subprocess.STDOUT, shell=True).decode()
    except subprocess.CalledProcessError as cpe:
        print(cpe)
    else:
        print(output)
        
    
def clean_peak_matrix(peak_matrix):
    """
    Clean up a multiple-experiment matrix of counts in peaks generated by HOMER's annotatePeaks.pl
    in order to prepare it for downstream processing
    """
    # split annotation columns
    peak_annotations = peak_matrix.iloc[:,:18]
    peak_matrix = peak_matrix.iloc[:,18:]    
    # clean up sample names
    peak_matrix.columns = [col.split(' ')[0].split('/')[-1] for col in peak_matrix.columns]
    # convert to int
    peak_matrix = peak_matrix.astype(int)
    peak_annotations.index.name = 'Peak_ID'
    peak_matrix.index.name = 'Peak_ID'
    return peak_annotations, peak_matrix    
    
    
def filter_self_overlap(peak_df, score_field='findPeaks Score', reverse=False, verbose=True):
    """
    Return a new peak DataFrame where only the highest-scoring peak in each set of self-overlapping peaks
    has been retained.
    """
    start_time = datetime.datetime.now() 
    if verbose:
        print('Filtering {} peaks'.format(peak_df.shape[0]))
    filtered_peaks = peak_df.copy()
    overlap_sets = []
    for overlap_pair in overlap_peaks(filtered_peaks, filtered_peaks):
        overlap_sets.append(set([overlap_pair[0], overlap_pair[1]]))
    multi_peaks = [overlap_set for overlap_set in overlap_sets if len(overlap_set) > 1]
    if verbose:
        print('Found {} multi-peaks'.format(len(multi_peaks)))
    worst_peaks = []
    for peakset in multi_peaks:
        if verbose:
            print(', '.join(['{:>15}: {:10}'.format(peak, filtered_peaks.loc[peak, score_field]) for peak in sorted(peakset, key=lambda x: filtered_peaks.loc[x, score_field], reverse=not(reverse))]))
        if reverse:
            worst_peaks.append(numpy.argmax(filtered_peaks.loc[peakset, score_field]))
        else:
            worst_peaks.append(numpy.argmin(filtered_peaks.loc[peakset, score_field]))

    filtered_peaks.drop(worst_peaks, axis=0, inplace=True)
    
    print('Kept {} peaks, discarded {}'.format(filtered_peaks.shape[0], peak_df.shape[0] - filtered_peaks.shape[0]))
    print('Done in {}'.format(datetime.datetime.now() - start_time))
    return filtered_peaks


def load_merged_annotations(original_homer_fname, annotated_homer_fname=''):
    """
    Combines the data from a HOMER peak file and a HOMER annotated peak file
    and returns it as a single DataFrame
    """
    # ToDo: Change chromosome designation from lowere case 'chrom' to 'Chr' for consistency
    start_time = datetime.datetime.now() 
    
    if not annotated_homer_fname:
        annotated_homer_fname = original_homer_fname.split('.')[0] + '_annotated.tsv'
    with open(original_homer_fname, 'rt') as orig_file:
        line = orig_file.readline()
        while line.startswith('#') and not line.startswith('#PeakID'):
            line = orig_file.readline()
        orig_file.seek(orig_file.tell()-len(line)+1)
        orig_peaks = pandas.read_csv(orig_file, sep='\t', index_col=0)
    
    annot_peaks = pandas.read_csv(annotated_homer_fname, sep='\t', index_col=0)
    
    joint_df = pandas.concat((orig_peaks, annot_peaks), axis=1)
    joint_df.drop(['Chr', 'Start', 'End'], axis=1, inplace=True)
    joint_df.rename(columns={'chr':'chrom'}, inplace=True)
    print('Done in {}'.format(datetime.datetime.now() - start_time))
    return joint_df


def overlap_peaks(peak_df1, peak_df2, min_overlap=0):
    """
    Returns a list of tuples consisting of the names of peaks that
    overlap by at least <min_overlap> as well as the region in which they overlap, i.e.:
    
    (peak_1_name, peak_2_name, overlap_start, overlap_end)
    """
#    start_time = datetime.datetime.now() 
    overlaps = []

    shared_chroms = set(peak_df1['Chr']).intersection(set(peak_df2['Chr']))
    for chrom in shared_chroms:
        
        this_chrom_df1 = peak_df1.loc[peak_df1['Chr'] == chrom]
        this_chrom_df2 = peak_df2.loc[peak_df2['Chr'] == chrom]
        tuples_1 = list(zip(this_chrom_df1.index, this_chrom_df1['Start'], this_chrom_df1['End']))
        tuples_2 = list(zip(this_chrom_df2.index, this_chrom_df2['Start'], this_chrom_df2['End']))
        #print(chrom, tuples_1, tuples_2)
        
        overlaps += intervaloverlaps.interval_overlaps(tuples_1, tuples_2, min_overlap=min_overlap)
    return overlaps
    

def filter_by_overlaps(peak_df1, peak_df2, min_overlap=0, inverse=False):
    """
    Return a copy of peak_df1 filtered to include only those peaks overlapping peak_df2
    by at least <min_overlap>.
    
    If <inverse> is true, return items not overlapping
    """
    overlaps = overlap_peaks(peak_df1, peak_df2, min_overlap=min_overlap)
       
    if inverse:
        result_df =  peak_df1.copy().drop([o[0] for o in overlaps]) #, peak_df2.copy().drop([o[1] for o in overlaps])
    else:
        result_df =  peak_df1.copy().loc[[o[0] for o in overlaps]] #, peak_df2.copy().loc[[o[1] for o in overlaps]]
    
    result_df = result_df.drop_duplicates()
    
    return result_df
    
## ToDo: Create a PeakSet class and implement all the importing exporting functions as methods

    
def export_df_to_homer(df, bed_filename):
    """
    Exports a DataFrame of peak info into the "HOMER" format.
    """
    start_time = datetime.datetime.now() 
    temp_peaks = df.copy()
#     temp_peaks['dummy'] = [''] * temp_peaks.shape[0]
    temp_peaks = temp_peaks.loc[:,['chrom', 'start', 'end', 'strand']]
    temp_peaks.to_csv(bed_filename, sep='\t', header=False, index=False)
    print('Done in {}'.format(datetime.datetime.now() - start_time))
    

def export_df_to_ucsc(df, bed_filename, track_name='', description='', use_score=True):
    """
    Exports a DataFrame of peak info into basic BED format suitable for loading into the UCSC genome browser
    """
    start_time = datetime.datetime.now() 
    print('Exporting to BED file {}{}'.format(bed_filename, ('', ' with track name "{}"'.format(track_name))[bool(track_name)]))
    temp_peaks = df.copy()
    temp_peaks['name'] = temp_peaks.index
    
    if 'chrom' in temp_peaks.columns:
        temp_peaks = temp_peaks.loc[:,['chrom', 'start', 'end', 'name', 'findPeaks Score', 'strand']]
    else:
        temp_peaks = temp_peaks.loc[:,['Chr', 'Start', 'End', 'name', 'Peak Score', 'Strand']]
    
    toolbox.establish_path(toolbox.parse_path(bed_filename)[0])
    with open(bed_filename, 'wt') as outfile:
        if track_name:
            if not description:
                description=track_name
            outfile.write('track name="{}" description="{}" useScore={}\n'.format(track_name, description, int(bool(use_score))))
        temp_peaks.to_csv(outfile, sep='\t', index=False, header=False)
    print('Done in {}'.format(datetime.datetime.now() - start_time))


def read_idr_peaks(idr_bed_fname):
    """
    Reads a BED-formatted peak output file from :param:`idr_bed_fname` and retuns a Dataframe with column headers
    
    Little tricky since the BED ouput appears to be undocumented but guessing for now that the 7th and 8th
    columns correspond to localIDR and globalIDR.
    
    If there are duplicate names (IDR appears to just output '.' in this field at the moment),
    will assign unique names using the HOMER scheme (CHROMOSOME-UNIQUE_INT)
    
    """
    peak_df = pandas.read_csv(idr_bed_fname, sep='\t')
    peak_df.columns = ['Chr', 'Start', 'End', 'Name', 'IDR score', 'Strand', 'localIDR', 'globalIDR', 'rep1_Start', 'rep1_End', 'rep1_Score', 'rep2_Start', 'rep2_End', 'rep2_Score']
    
    peak_df = assign_unique_peak_names(peak_df)
        
    return peak_df


def assign_unique_peak_names(peak_df):
    """
    Given a dataframe of peaks with a column called 'Name', first checks if all peak names are unique.
    If not, assigns unique names to each peak in that column using the HOMER scheme (CHROMOSOME-UNIQUE_INT)
    """
    if len(set(peak_df['Name'])) != peak_df.shape[0]:

        for chrom in set(peak_df['Chr']):
            chrom_rows = peak_df['Chr'] == chrom
            peak_df.loc[chrom_rows, 'Name'] = ['{}-{}'.format(chrom, num) for num in range(1, sum(chrom_rows)+1)]
    
    return peak_df
    
    
def write_to_bed(peak_df, output_fname):
    """
    Write a peak dataframe to BED-6 format
    """
    peak_df.iloc[:,:6].to_csv(output_fname, sep='\t', index=None, header=None)
    
    
def send_out_for_motif_analysis(peak_df, analysis_name, species, background_df=None, size='given', mask=True, lengths=[12,10,8], write_script=False, genome_build='', cores=NUM_CORES, additional_options=None):
    """
    Generate temp files and create a script to run motif analysis on the specified Peak Dataframe.
    """
    #start_time = datetime.datetime.now()
    # Export dataframe as bed file
    if not genome_build:
        genome_build = GENOME_NAMES[species]
        
    os.makedirs(TMP_DIR, exist_ok=True)
    peak_fname = os.path.join(TMP_DIR, 'peak_export_{}.bed'.format(toolbox.random_identifier(32)))
    write_to_bed(peak_df, peak_fname)
    
    if background_df is not None:
        bg_fname = os.path.join(TMP_DIR,'bg_export_{}.bed'.format(toolbox.random_identifier(32)))
        write_to_bed(background_df, bg_fname)
    
    # findMotifsGenome.pl <peak/BED file> <genome> <output directory> -size # [options]
    cmd_line = ['findMotifsGenome.pl',
                peak_fname,
                genome_build,
                toolbox.home_path('{}/motifs/{}'.format(species, analysis_name)),
                '-size', str(size), '-p', str(cores), '-len', ','.join([str(l) for l in lengths])]
    if mask:
        cmd_line += ['-mask']
        
    if background_df is not None:
        cmd_line += ['-bg', bg_fname]
    
    if additional_options:
        cmd_line += ' '.split(additional_options)

    if write_script:
        script_fname = toolbox.home_path('{}/motifs/analyze_{}.sh'.format(species, analysis_name))
        print('Writing commands to {}'.format(script_fname))
        with open(script_fname, 'wt') as script_file:
            script_file.write('#!/bin/bash\n')
            script_file.write('rm {}\n'.format(script_fname))
            script_file.write(' '.join(cmd_line) + '\n')
            script_file.write('rm {}\n'.format(peak_fname))
            if background_df is not None:
                script_file.write('rm {}\n'.format(bg_fname))
    else:
        print('Running analysis ...')
        try:
            output = subprocess.check_output(cmd_line, stderr=subprocess.STDOUT).decode()
        except CalledProcessError as cpe:
            output = str(cpe)

        print(output)
    
        os.remove(peak_fname)
        if background_df is not None:
            os.remove(bg_fname)
    #print 'Done in {}'.format(datetime.datetime.now() - start_time)

def venn_2_dfs(df_1, df_2, name_1, name_2, ax=None):
    """
    Render a 2-way Venn diagram of overlaps between two peak Dataframes.
    """
    overlap_size = filter_by_overlaps(df_1, df_2).shape[0]
    matplotlib_venn.venn2(subsets={'10':df_1.shape[0]-overlap_size, '01':df_2.shape[0]-overlap_size, '11':overlap_size},
                         set_colors=('c', 'm'), set_labels=(name_1, name_2), ax=ax)


def venn_3_dfs(df_1, df_2, df_3, name_1, name_2, name_3, ax=None):
    """
    Render a 3-way Venn diagram of overlaps between three peak Dataframes.
    """
    df_1_and_df_2 = filter_by_overlaps(df_1, df_2)
    df_1_and_df_3 = filter_by_overlaps(df_1, df_3)
    df_2_and_df_3 = filter_by_overlaps(df_2, df_3)
    all_3 = filter_by_overlaps(df_1_and_df_2, df_3)
    
    matplotlib_venn.venn3(subsets = {'100':df_1.shape[0] - df_1_and_df_2.shape[0] - df_1_and_df_3.shape[0] + all_3.shape[0],
                                     '010':df_2.shape[0] - df_1_and_df_2.shape[0] - df_2_and_df_3.shape[0] + all_3.shape[0],
                                     '001':df_3.shape[0] - df_1_and_df_3.shape[0] - df_2_and_df_3.shape[0] + all_3.shape[0],
                                     '110':df_1_and_df_2.shape[0] - all_3.shape[0],
                                     '011':df_2_and_df_3.shape[0] - all_3.shape[0],
                                     '101':df_1_and_df_3.shape[0] - all_3.shape[0],
                                     '111':all_3.shape[0]},
                                     set_colors=('c', 'm', 'y'),
                                     set_labels=(name_1, name_2, name_3),
                                     ax=ax)


def dataframe_quantile_filter(peak_df, variable='findPeaks Score', quantile_range=(0.75,1)):
    """
    Return a copy of <peak_df> containing only peaks with <variable> in the
    specified <quantile_range>.
    """
    start_time = datetime.datetime.now() 
    assert len(quantile_range) == 2
    assert quantile_range[0] >= 0 and quantile_range[0] <= 1
    assert quantile_range[1] >= 0 and quantile_range[1] <= 1
    return peak_df.sort_values(by=[variable], ascending=True).iloc[int(peak_df.shape[0] * quantile_range[0]):int(peak_df.shape[0] * quantile_range[1])]


def enhancers(peak_df, threshold=1000):
    return peak_df[numpy.abs(peak_df['Distance to TSS']) > threshold]


def check_for_self_overlap(peak_df):
    """
    Returns a Boolean indicating whether or not any peaks in <peak_df>
    overlap themselves.
    """
    start_time = datetime.datetime.now() 
    for chrom, group in peak_df.groupby('chrom'):
        it = intervaltree.IntervalTree.from_tuples(list(zip(group['start'], group['end'])))
        old_size = len(it)
        it.split_overlaps()
        if len(it) != old_size:
            return True
    return False
    

def scatter_peaks(peakset1,
                  peakset2,
                  name1,
                  name2,
                  plot_variable='Normalized Tag Count',
                  unit='Normalized Tag Count',
                  transform=None,
                  infer_zeros=False,
                  stat_func=None,
                  stat_func_name='',
                  color_by_density=False,
                  cmap='Reds',
                  color='r',
                  plot_size=4,
                  marker_size=5,
                  marker='o',
                  ax=None):
    start_time = datetime.datetime.now() 
    this_overlap = overlap_peaks(peakset1, peakset2, 0)
    
    x_data = peakset1.loc[[o[0] for o in this_overlap], plot_variable]
    y_data = peakset2.loc[[o[1] for o in this_overlap], plot_variable]
        
    if infer_zeros:
        non_overlapping1 = filter_by_overlaps(peakset1, peakset2, 0, inverse=True)
        non_overlapping2 = filter_by_overlaps(peakset2, peakset1, 0, inverse=True)
        x_data = pandas.concat((x_data, pandas.Series(numpy.zeros(non_overlapping2.shape[0])), non_overlapping1.loc[:, plot_variable]), axis=0)
        y_data = pandas.concat((y_data, non_overlapping2.loc[:, plot_variable], pandas.Series(numpy.zeros(non_overlapping1.shape[0]))), axis=0)
    
    if transform:
        x_data = transform(x_data)
        y_data = transform(y_data)
    
    seaborn.set_style('white')
    if not ax:
        fig, ax = plt.subplots(1, figsize=(plot_size,plot_size))

    if color_by_density:
        xy = numpy.vstack([x_data,y_data])
        z = gaussian_kde(xy)(xy)
        idx = z.argsort()
        x_data, y_data, z = x_data[idx], y_data[idx], z[idx]
        
    
        ax.scatter(x=x_data,
                   y=y_data,
                   marker=marker, cmap=cmap, c=z, s=marker_size, edgecolor='')
    else:
        ax.scatter(x=x_data,
                   y=y_data,
                   marker=marker, c=color, s=marker_size, edgecolor='')
        
    ax.set_xlabel('{} {}'.format(name1, unit))
    ax.set_ylabel('{} {}'.format(name2, unit))
    # make axes square
    biggest_lim = max(ax.get_ylim()[1], ax.get_xlim()[1])
    ax.set_xlim(0, biggest_lim)
    ax.set_ylim(0, biggest_lim)
    
    if stat_func:
        print('{} vs {}, {}: {:>.3}'.format(name1, name2, stat_func_name, stat_func(x_data, y_data)))
        ax.text(x=(ax.get_xlim()[1] - ax.get_xlim()[0]) * 0.1 - ax.get_xlim()[0],
                y=(ax.get_ylim()[1] - ax.get_ylim()[0]) * 0.9 - ax.get_ylim()[0],
                s='{}: {:>.3}'.format(stat_func_name, stat_func(x_data, y_data)))
    print('Done in {}'.format(datetime.datetime.now() - start_time))
    
    
def filter_by_strength(peak_df, tag_threshold=16):
    """Given a DataFrame of HOMER peaks, return a new dataframe containing only
    those peaks above the tag threshold"""
    
    original_count = peak_df.shape[0]
    new_df=peak_df.loc[peak_df['Normalized Tag Count'] >= tag_threshold]
    new_count = new_df.shape[0]
    print('{} peaks out of {} retained with tags >= {}'.format(new_count, original_count, tag_threshold))
    return new_df
    

def kill_duplicates(df):
    """
    Remove duplicate entries from a DataFrame (keeps the first one).
    """
    old_count = df.shape[0]
    new_df = df.loc[~df.duplicated()]
    new_count = new_df.shape[0]
    if new_count <= old_count:
        print('Removed {} of {} duplicate index entries, {} remaining'.format(old_count - new_count, old_count, new_count))
    return new_df    
