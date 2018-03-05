import os
import itertools
import numpy
import scipy
import pandas
import seaborn
import matplotlib.pyplot as plt

from pgtools import toolbox

PSEUDO_COUNT = 1
EXPRESSION_THRESHOLD = 1
FIG_EXTS = ['pdf', 'png']
PNG_DPI = 600

def load_and_clean(datafile):
    exp_data = pandas.read_csv(datafile, sep='\t', index_col=0).T
    
    exp_data.index.name = 'Sample'
    # trim sample names
    new_index = []
    for i in range(exp_data.shape[0]):
        index_item = exp_data.index[i]
        
        if i >= 7:
            if index_item.find(' reads') > -1:
                index_item = index_item[:index_item.find(' reads')]

            if index_item.find('/') > -1:
                index_item = index_item.split('/')[-1]
            
        new_index.append(index_item)
        
    exp_data.index = new_index

    exp_data.columns.name='Entrez mRNA ID'
    return exp_data


def trim_rna_file(input_filename, output_filename='', fix_names=True, transcript_to_gene=False, sep='\t'):
    """
    Given the filename of a HOMER-output RNA-seq DataFrame, generate a 
    new file containing a new dataframe with the gene info columns (0-6)
    removed. <output_filename> defaults to input_filename with "_trimmed"
    appended to the filename mantissa.
    
    If :param:`transcript_to_gene` is True, replace the refseq Transcript ID with the gene name from the annotation
    """
    
    path, prefix, suffix = toolbox.parse_path(input_filename)
    toolbox.establish_path(path)
        
    rna_data = pandas.read_csv(input_filename, sep=sep, index_col=0)
    
    if transcript_to_gene:
        gene_names = [anno.split('|')[0] for anno in rna_data.iloc[:,6]]
        rna_data.index = gene_names
        
    rna_data = rna_data.iloc[:,7:]
    
    # print(rna_data.columns)
    
    if fix_names:
        rna_data.columns = [col.replace('-','_').replace('.','_') for col in rna_data.columns]
        
    # print(rna_data.columns)
    
    rna_data.columns = [col.strip('/').split('/')[-1].strip() for col in rna_data.columns]
    # print(rna_data.columns)
    rna_data.columns = [(col, col.split(' FPKM')[0])[' FPKM' in col] for col in rna_data.columns]
    # print(rna_data.columns)
    rna_data.columns = [(col, col.split(' TPM')[0])[' TPM' in col] for col in rna_data.columns]
    # print(rna_data.columns)
    rna_data.columns = [(col, col.split(' (')[0])[' total)' in col] for col in rna_data.columns]
    # print(rna_data.columns)
    
    if not output_filename:
        output_filename = os.path.join(path, '{}{}{}.{}'.format(prefix, '_trimmed', ('', '_gene_name')[transcript_to_gene], suffix))
    
    rna_data.to_csv(output_filename, sep='\t')

    
def convert_rpkm_to_tpm(rpkm_data):
    """
    Given a trimmed DataFrame of RNA-seq data in RPKM (with genes on rows
    and samples on columns), return a new dataframe the the RPKM values
    converted to transcripts per million (TPM)
    """
    return rpkm_data / rpkm_data.sum(axis=0) * 1e6


def filter_by_type(raw_data, length_threshold=200):
    """
    Retain only protein-coding transcripts and ncRNA transcripts with length >= length_threshold (lncRNA)
    """
    filtered_data = raw_data.loc[:, [raw_data.loc['Annotation/Divergence'][i].split('|')[-1] == 'protein-coding'
                             or (raw_data.loc['Annotation/Divergence'][i].split('|')[-1] == 'ncRNA'
                                 and raw_data.loc['Length'][i] >= length_threshold) for i in range(raw_data.shape[1])]]
    print('Initial transcripts: {}'.format(raw_data.shape[1]))
    print('Retaining only protein-coding and ncRNA transcripts with length >= {}'.format(length_threshold))
    print('\tRemoved {} transcripts'.format(raw_data.shape[1] - filtered_data.shape[1]))
    print('{} transcripts remaining'.format(filtered_data.shape[1]))
    return filtered_data


def filter_by_expression_magnitude(raw_data, magnitude_threshold=1):
    """
    Remove any transcripts not expressed at at least <magnitude_threshold> in one or more samples.
    """
    data_rows = raw_data.index[:]
    print('Initial transcripts: {}'.format(raw_data.shape[1]))
    filtered_data = raw_data.loc[:,(raw_data.loc[data_rows] >= magnitude_threshold).any(axis=0)]
    print('Removed {} transcripts with magnitude < {} across all samples'.format(raw_data.shape[1] - filtered_data.shape[1], magnitude_threshold))
    print('{} transcripts remaining'.format(filtered_data.shape[1]))
    return filtered_data


def correlated_columns(df):
    """
    Since the Pandas DataFrame.corr() method has stopped working, I create my own
    """
    sample_corrs = pandas.DataFrame(numpy.zeros((df.shape[1], df.shape[1])), index=df.columns, columns=df.columns)
    for col1, col2 in itertools.combinations(df.columns, 2):
        pcc = scipy.stats.pearsonr(df[col1], df[col2])[0]
        sample_corrs.loc[col1, col2] = pcc
        sample_corrs.loc[col2, col1] = pcc
    for col in df.columns:
        sample_corrs.loc[col, col] = 1.0
    return sample_corrs


def scatter_rna(rna_df, dataset1, dataset2, name1='', name2='', transform=None, stat_func=None, stat_func_name='', magnitude_threshold=0, threshold_type='',
                  cmap='', color='r', plot_size=4, marker_size=10, marker='o', units='Log_2 TPM', density_gamma=1, output_fname_prefix='', 
                  lims=None, ticks=None, visible_ticks=True,
                  coloring_sets=None,
                  annotations=None, annotation_padding=0.2, annotation_color='k', annotation_font_size=8,
                  annotation_linewidth=1, show_diagonal=False, diagonal_kwargs={}, fig=None, ax=None):
    """
    Generates a scatterplot of expression values between matched sequences of expression data :dataset1: and :dataset2:
    
    :name1: label for dataset1
    :name2: label for dataset2
    :transform: (optional) a function to apply to every value in each dataset prior to plotting.
    :stat_func: (optional) a summary statistical function which will be passed both datasets.
    :stat_func_name: (optional) the name of the resulting statistic
    :magnitude_threshold: (optional) only plot data above this threshold (after transformation, if any)
    :threshold_type: (optional) can be 'and' or 'or'. For 'and', exclude any points which are not above the threshold in _both_ datasets.
        For 'or' exclude any points below the threshold in _either_ dataset.
    :cmap: (optional) the name of a built-in matplotlib colormap to use for a density-based coloring of points. If empty, just use a plain color
    :color: (optional) if :cmap: is not specified, use this single color to render the points. Defaults to red.
    :plot_size: (optional) the size of each figure dimension, in inches.
    :marker_size: (optional) the size of each point marker, in points. Defaults to 10.
    :marker: (optional) any valid matplotlib marker style to use for the point markers. Defaults to 'o' (filled circle).
    :units: (optional) the name of the resulting units of expression that will be appended to each dataset name to label the axes. Defaults to 'Log_2 TPM'
    :density_gamma: (optional) the density color mapping will be raised to this power. So numbers less than 1 reduce contrast and move values to the denser
        end, and values greater than 1 increase contrast and move values to the sparser end.
    :output_fname_prefix: (optional). If present, save a PNG and PDF having this prefix.
    :lims: (optional): force the axes to have the specified range. If not specified, use the larger of the automatically-determined axis sizes.
    :ticks: (optional): a sequence of locations to place ticks on both axes.
    :coloring_sets: an iterable of tuples. Each tuple should consist of a color code paired with a list of genes to which the color should be applied. Not compatible with :cmap:.
    :annotated_genes: an iterable of tuples containing (gene_name, x_offset, y_offset) where x and y offsetts give the coordinate shifts for the label relative to the gene location
    :show_diagonal: Whether or not to draw a line across the diagonal. Default False.
    :diagonal_kwargs: Keyword arguments to pass to the plot function that draws the diagonal.
    :fig: (optional) matplotlib Figure object to use.
    :ax: (optional) matplotlib Axes object to use. 
    """
    if (fig or ax) and (not fig and ax):
        raise ValueError('If passing a fig or ax object, must pass both!')
        
    if not (fig and ax):
        seaborn.set_style('white')
        fig, ax = plt.subplots(1, figsize=(plot_size,plot_size))
    x_data = rna_df.loc[:,dataset1]
    y_data = rna_df.loc[:,dataset2]
    
    if not name1:
        name1 = dataset1
    if not name2:
        name2 = dataset2
    
    if transform:
        x_data = transform(x_data)
        y_data = transform(y_data)
    
    if threshold_type == 'or':
        # keep only genes with > threshold expression in at least one dataset
        print('Keeping only transcripts with >= {} expression in at least one dataset'.format(magnitude_threshold))
        kept_genes = set(x_data[x_data >= magnitude_threshold].index).union(set(y_data[y_data >= magnitude_threshold].index))
    elif threshold_type == 'and':
        print('Keeping only transcripts with >= {} expression in both datasets'.format(magnitude_threshold))
        # keep only genes with > threshold expression in at least one dataset
        kept_genes = set(x_data[x_data >= magnitude_threshold].index).intersection(set(y_data[y_data >= magnitude_threshold].index))
    elif threshold_type == '':
        kept_genes = rna_df.index
    else:
        raise ValueError('Unknown threshold type: {}'.format(threshold_type))
        
    x_data = x_data.loc[kept_genes]
    y_data = y_data.loc[kept_genes]
    print('Kept {} transcripts, discarded {}.'.format(len(kept_genes), rna_df.shape[0] - len(kept_genes)))
    
    if stat_func:
        stat_result = stat_func(x_data, y_data)
                
    if cmap:
        xy = numpy.vstack([x_data,y_data])
        z = scipy.stats.gaussian_kde(xy)(xy)**density_gamma
        idx = z.argsort()
        x_data, y_data, z = x_data[idx], y_data[idx], z[idx]
        
    
        ax.scatter(x=x_data,
                   y=y_data,
                   marker=marker, cmap=cmap, c=z, s=marker_size, edgecolor='')
    else:
        if coloring_sets:
            remaining_genes = set(kept_genes)
            for set_color, set_genes in coloring_sets:
                remaining_genes = remaining_genes.difference(set_genes)
            # plot the remaining genes
            ax.scatter(x=x_data.loc[remaining_genes],
                       y=y_data.loc[remaining_genes],
                       marker=marker, c=color, s=marker_size, edgecolor='')

                
            for set_color, set_genes in coloring_sets:
                ax.scatter(x=x_data.loc[set_genes],
                       y=y_data.loc[set_genes],
                       marker=marker, c=set_color, s=marker_size, edgecolor='')
            

        else:
            ax.scatter(x=x_data,
                       y=y_data,
                       marker=marker, c=color, s=marker_size, edgecolor='')
                       
    if annotations:
        for gene_name, x_offset, y_offset in annotations:
            if gene_name in x_data.index and gene_name in y_data.index:
                gene_x = x_data[gene_name]
                gene_y = y_data[gene_name]
            
                # Compute padding components using Pythogorean theorem 
                pointer_length = numpy.sqrt(x_offset**2 + (y_offset)**2)
                if pointer_length > annotation_padding * 2:
                    correction_factor = annotation_padding / pointer_length
                    padding_x = x_offset * correction_factor
                    padding_y = y_offset * correction_factor
                else:
                    padding_x = 0
                    padding_y = 0                

                text_x = gene_x + x_offset
                text_y = gene_y + y_offset
                ax.text(x=text_x, y=text_y, s=gene_name, fontsize=annotation_font_size)
                ax.plot((gene_x+padding_x, text_x - padding_x), (gene_y + padding_y, text_y-padding_y),
                        color=annotation_color, linewidth=annotation_linewidth)            
    
    ax.set_xlabel('{} {}'.format(name1, units))
    ax.set_ylabel('{} {}'.format(name2, units))
    
    # make axes square
    if not lims:
        biggest_lim = max(ax.get_ylim()[1], ax.get_xlim()[1])
        lims = (0, biggest_lim)
        
    ax.set_xlim(*lims)
    ax.set_ylim(*lims)
    
    if ticks:
        ax.set_xticks(ticks)
        ax.set_yticks(ticks)
        
    plt.setp(ax.get_xticklabels(), visible=visible_ticks)
    plt.setp(ax.get_yticklabels(), visible=visible_ticks)
    
    if show_diagonal:
        ax.plot(*lims, **diagonal_kwargs)
    
    
    if stat_func:
        print('{} vs {}, {}: {:>.3}'.format(name1, name2, stat_func_name, stat_func(x_data, y_data)))
        ax.text(x=(ax.get_xlim()[1] - ax.get_xlim()[0]) * 0.1 + ax.get_xlim()[0],
                y=(ax.get_ylim()[1] - ax.get_ylim()[0]) * 0.9 + ax.get_ylim()[0],
                s='{}: {:>.3}'.format(stat_func_name, stat_result))
    
    if output_fname_prefix:
#        toolbox.establish_path(toolbox.parse_path(output_fname_prefix)[0])
        # Save plot
        for fig_ext in FIG_EXTS:
            figure_fname = '{}.{}'.format(output_fname_prefix, fig_ext)
            print('Saving figure to {} ...'.format(figure_fname))
            fig.savefig(figure_fname, bbox_inches='tight', dpi=PNG_DPI)
        # Save data as CSV file
        data_fname = '{}_data.csv'.format(output_fname_prefix)
        print('Saving raw data to {}'.format(data_fname))
        pandas.DataFrame({'{} ({})'.format(name1, units):x_data, '{} ({})'.format(name2, units):y_data}, index=x_data.index).to_csv(data_fname, index=False)

