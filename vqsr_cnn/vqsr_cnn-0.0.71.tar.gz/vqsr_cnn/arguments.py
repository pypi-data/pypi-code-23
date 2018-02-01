import argparse
import numpy as np
import keras.backend as K

from . import defines
from . import tensor_maps

def parse_args():
    parser = argparse.ArgumentParser()

    # Tensor defining dictionaries
    parser.add_argument('--tensor_map', default='read_tensor',
                        help='Key which looks up the map from tensor channels to their meaning.')
    parser.add_argument('--input_symbols', default=dna_symbols,
                        help='Dict mapping input symbols to their index within input tensors.')
    parser.add_argument('--labels', default=snp_indel_labels,
                        help='Dict mapping label names to their index within label tensors.')

    # Tensor defining arguments
    parser.add_argument('--batch_size', default=32, type=int,
                        help='Mini batch size for stochastic gradient descent algorithms.')
    parser.add_argument('--read_limit', default=128, type=int,
                        help='Maximum number of reads to load.')
    parser.add_argument('--window_size', default=128, type=int,
                        help='Size of sequence window to use as input, typically centered at a variant.')
    parser.add_argument('--channels_last', default=False, dest='channels_last', action='store_true',
                        help='Store the channels in the last axis of tensors, tensorflow->true, theano->false')
    parser.add_argument('--base_quality_mode', default='phot', choices=['phot', 'phred', '1hot'],
                        help='How to treat base qualities, must be in [phot, phred, 1hot]')

    # Annotation arguments
    parser.add_argument('--annotations', help='Array of annotation names, initialised via annotation_set argument')
    parser.add_argument('--annotation_set', default='gatk', choices=defines.ANNOTATIONS.keys(),
                        help='Key which maps to an annotations list (or None for architectures that do not take annotations).')

    # Genomic area of interest
    parser.add_argument('--start_pos', default=0, type=int,
                        help='Genomic position to start from, helpful for parallelization.')
    parser.add_argument('--end_pos', default=0, type=int,
                        help='Genomic position to end at, helpful for parallelization.')
    parser.add_argument('--chrom', help='Specific chromosome to load, helpful for parallelization.')

    # Input files and directories: vcfs, bams, beds, hd5, fasta
    parser.add_argument('--architecture', default='',
                        help='A json file specifying semantics and architecture of a neural net.')
    parser.add_argument('--bam_file',
                        help='Path to a BAM file to train from or generate tensors with.')
    parser.add_argument('--train_vcf',
                        help='Path to a VCF that has verified true calls from NIST, platinum genomes, etc.')
    parser.add_argument('--negative_vcf',
                        help='Haplotype Caller or VQSR generated VCF with raw annotation values [and quality scores].')
    parser.add_argument('--output_vcf', default=None,
                        help='Optional VCF to write to.')
    parser.add_argument('--bed_file',
                        help='Bed file specifying high confidence intervals associated with args.train_vcf.')
    parser.add_argument('--dataset',
                        help='Directory of tensors, must be split into test/valid/train sets with directories for each label within.')
    parser.add_argument('--reference_fasta',
                        help='The reference FASTA file (e.g. HG19 or HG38).')

    # Run specific arguments
    parser.add_argument('--id', default='no_id',
                        help='Identifier for this run, user-defined string to keep experiments organized.')
    parser.add_argument('--random_seed', default=12878, type=int,
                        help='Random seed to use throughout run.  Always use np.random.')

    # Parse, print, set annotations and seed
    args = parser.parse_args()
    args.annotations = annotations_from_args(args)
    np.random.seed(args.random_seed)
    print('Arguments are', args)

    return args


def annotations_from_args(args):
    if args.annotation_set and args.annotation_set in defines.ANNOTATIONS:
        return defines.ANNOTATIONS[args.annotation_set]
    return None


def tensor_shape_from_args(args):
    in_channels = len(tensor_maps.get_tensor_channel_map_from_args(args))
    if K.image_data_format() == 'channels_last':
        tensor_shape = (args.read_limit, args.window_size, in_channels)
    else:
        tensor_shape = (in_channels, args.read_limit, args.window_size)
    return tensor_shape

