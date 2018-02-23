# from intervaltree import Interval, IntervalTree
from lib.parsers import generate_snvs
from collections import namedtuple
import numpy as np


FILE_DELIMITER = ","


def sample(parser):
    """ Return various data regarding overall-editing in one or more samples.

    hekase sample --gtf   Homo_sapiens.GRCh38.90.gtf                   \
                  --names SRR2087305,SRR1998058,SRR2087291             \
                  --vcf   SRR2087305.vcf,SRR1998058.vcf,SRR2087291.vcf \
                  --bam   SRR2087305,SRR1998058,SRR2087291
    """

    """
    parser.add_argument('-g', "--gtf",
                        type=str,
                        required=True,
                        help='')

    parser.add_argument('-g', "--bed",
                        type=str,
                        required=True,
                        help='')
    """

    parser.add_argument('-n', "--names",
                        type=str,
                        required=True,
                        help='')

    parser.add_argument('-b', "--bam",
                        type=str,
                        required=True,
                        help='')

    parser.add_argument('-v', "--vcf",
                        type=str,
                        required=True,
                        help='')

    parser.add_argument('-c', "--coverage",
                        type=int,
                        required=True,
                        help='')

    args = parser.parse_args()

    # Get sites
    # Get coverage


def gene(parser):
    """ Return various data regarding overall-editing in one or more samples.

    hekase sample --gtf   Homo_sapiens.GRCh38.90.gtf                   \
                  --names SRR2087305,SRR1998058,SRR2087291             \
                  --vcf   SRR2087305.vcf,SRR1998058.vcf,SRR2087291.vcf \
                  --bam   SRR2087305,SRR1998058,SRR2087291
    """

    """
    parser.add_argument('-g', "--gtf",
                        type=str,
                        required=True,
                        help='')

    parser.add_argument('-g', "--bed",
                        type=str,
                        required=True,
                        help='')


    parser.add_argument('-n', "--names",
                        type=str,
                        required=True,
                        help='')

    parser.add_argument('-b', "--bam",
                        type=str,
                        required=True,
                        help='')
    """

    parser.add_argument('-v', "--vcf",
                        nargs='*',
                        type=str,
                        required=True,
                        help='')

    # parser.add_argument('-c', "--coverage",
    #                     type=int,
    #                     required=True,
    #                     help='')

    args = parser.parse_args()

    from lib.parsers import GenomicIntervalTree
    from lib.parsers import VCFIntervalTree
    from lib.parsers import get_coverage

    # Get sites
    # Get coverage
    # Parse vcf file groups.
    # Get genes
    # Make interval tree of vcf locations

    vcf_groups = []

    # Build interval tree from all VCF files.
    for vcf_group in args.vcf:

        vcf_files = vcf_group.split(FILE_DELIMITER)
        vcf_it_obj = VCFIntervalTree()

        for vcf_file in vcf_files:
            print(vcf_file)
            for chrom, pos, id, ref, alt, qual, fil, info in generate_snvs(vcf_file):
                strand = "+" if ref == "A" else "-"
                coverage = get_coverage(info)
                sub = (ref, alt)
                data = (vcf_files, sub, coverage)
                vcf_it_obj.add_snv(strand, chrom, int(pos), data)

            vcf_groups.append(vcf_it_obj)

    print("??")


def make_groups(dict_of_groups, labels=None):
    """
    { "bam": ["bam1,bam2", "bam3,bam4"]
    {
        "group_1": {"vcf":[vcf_1, vcf_2], "bam":[bam_1, bam_2]}
        "group_2": {"vcf":[vcf_3, vcf_4], "bam":[bam_3, bam_4]}
    }

    :param dict_of_groups:
    :return:
    """

    sorted_keys = sorted(dict_of_groups)

    if labels:
        labels = ",".split(FILE_DELIMITER)
    else:
        first_label_groups = len(dict_of_groups[sorted_keys[0]])
        labels = []
        for i in range(1, first_label_groups+1):
            labels.append("Group_%s" % i)

    group_names = []
    for dict_key in sorted(dict_of_groups):
        group_names.append(dict_key)

    print(group_names)

    GroupObj = namedtuple('GroupObj', group_names)

    g = GroupObj(["1", "3"], ["2", "4"])
    print(g)
    print(GroupObj)

    groups = []
    for i in range(len(labels)):
        tmp_list = []
        for sorted_key in sorted_keys:
            tmp_list.append(dict_of_groups[sorted_key][i].split(","))

        print(tmp_list)

        groups.append(GroupObj(*tmp_list))
    return groups


def region_diff(parser):
    """ Determine if two regions have differential editing.

    :param parser:
    :return:
    """
    # Parse BED file
    # Parse regions

    parser.add_argument('-g', "--groups",
                        type=str,
                        default=False,
                        help='')

    parser.add_argument('-v', "--vcf",
                        nargs='*',
                        type=str,
                        required=True,
                        help='')

    parser.add_argument("--bed",
                        type=str,
                        required=True,
                        help='')

    parser.add_argument("--bam",
                        nargs='*',
                        type=str,
                        required=True,
                        help='')

    args = parser.parse_args()

    from lib.parsers import GenomicIntervalTree
    from lib.parsers import VCFIntervalTree
    from lib.parsers import get_coverage
    from pysam import AlignmentFile

    # for group_name, vcf_group, bam_group in group_file_tuples:
    #

    # Make a vcf of all
    vcf_groups = []
    vcf_dict = {}
    bam_dict = {}
    bam_obj = {}
    grps = {"bam": args.bam, "vcf": args.vcf}
    group_obj_list = make_groups(grps)

    bam_file_dict = {}
    for bam_group in args.bam:
        for bam_file_name in bam_group.split(FILE_DELIMITER):
            bam_file_dict.update({bam_file_name: AlignmentFile(bam_file_name, "rb")})

    # Build a data structure of groups and different file types.

    for group in group_obj_list:
        for vcf_file in group.vcf:
            for chrom, pos, id, ref, alt, qual, fil, info in generate_snvs(vcf_file):
                strand = "+" if ref == "A" else "-"
                coverage = get_coverage(info)
                sub = (ref, alt)
                # data = (vcf_files, sub, coverage)
                vcf_entry = (chrom, pos, ref, alt)

                try:
                    vcf_dict[vcf_entry].append(vcf_file)
                except KeyError:
                    vcf_dict.update({vcf_entry: [vcf_file]})

    chromosome_dicts = {}
    vcf_it_obj = VCFIntervalTree()
    for varient in vcf_dict:
        chrom, pos, ref, alt, = varient
        strand = "+" if ref == "A" else "-"
        vcf_it_obj.add_snv(strand, chrom, int(pos), vcf_dict[varient])

    cutoff = 9
    # For feature in bed file
    for line in open(args.bed):
        s = line.split()
        chrom = s[0]
        start = int(s[1])
        stop = int(s[2])
        strand = s[5]

        # Return all SNPs detected across all samples
        query = vcf_it_obj.get_snvs_within_range(chrom, strand, start, stop)

        choice_list = []
        for e in query:
            pos, pos_plus_one = e[:2]

            query_groups = []
            for group in group_obj_list:
                # tmp_bam_cnt = []
                tmp_group_counts = []
                for bam_file in group.bam:

                    tmp_bam_cnt = []
                    for read in bam_file_dict[bam_file].fetch(chrom, pos, pos + 1):
                        try:
                            not_edited = ref == read.seq[pos - read.pos]
                            tmp_bam_cnt.append(not_edited)
                            # group_dict[group][bam_name].append(not_edited)
                            # print(not_edited, pos, read.pos, pos - read.pos)
                        except IndexError:
                            pass
                    tmp_group_counts.append((tmp_bam_cnt.count(False), len(tmp_bam_cnt)))

                query_groups.append(tmp_group_counts)

            g1 = query_groups[0]
            g2 = query_groups[1]

            g1_cnt = sum([g1i[1] for g1i in g1])
            g2_cnt = sum([g2i[1] for g2i in g2])

            g1_editing_cnt = sum([g1i[0] for g1i in g1])
            g2_editing_cnt = sum([g2i[0] for g2i in g2])

            if g1_cnt > cutoff and g2_cnt > cutoff:
                if g1_editing_cnt*0.1 > g2_editing_cnt:
                    choice_list.append(1)
                elif g2_editing_cnt*0.1 > g1_editing_cnt:
                    choice_list.append(-1)
                else:
                    choice_list.append(0)
            else:
                    choice_list.append(0)

        print(sum(choice_list))



def editing_site_diff(parser):
    """ Find differentially edited editing sites.

python3 /home/tyler/Documents/Projects/Hekase/hekase.py esdiff --groups heart,liver
--vcf ERR315435.all_editing_sites.vcf,ERR315389.all_editing_sites.vcf,ERR315430.all_editing_sites.vcf,ERR315356.all_editing_sites.vcf
ERR315327.all_editing_sites.vcf,ERR315451.all_editing_sites.vcf,ERR315463.all_editing_sites.vcf,ERR315394.all_editing_sites.vcf


return "\t".join(map(str, (self.query_name,                  ERR315435.6662877
                               self.flag,                    99
                               self.reference_id,            0
                               self.reference_start,         150731373
                               self.mapping_quality,         60
                               self.cigarstring,             101M
                               self.next_reference_id,       0
                               self.next_reference_start,    150731584
                               self.query_alignment_length,  101
                               self.query_sequence,          CGAGACTCCGTCTCAAAAAACAAAACAAAACTGAAAAGTAATCAACTAAATACTTTTAAACTATAATATTCTATACACTTTTGATGATAGCCATGTATTAT
                               self.query_qualities,         array('B', [19, 11, 21, 22, 23, 25, 29, 30, 29, 24, 32, 31, 30, 30, 30, 29, 29, 29, 29, 29, 29, 30, 29, 29,
                               29, 29, 30, 29, 29, 29, 29, 31, 30, 29, 29, 29, 29, 30, 30, 30, 29, 30, 29, 30, 29, 29, 31, 30, 29, 29, 30, 30, 29, 31, 29, 29, 29, 30, 29,
                               29, 29, 32, 30, 31, 31, 31, 30, 32, 30, 30, 30, 30, 32, 30, 32, 30, 31, 30, 31, 31, 31, 31, 31, 31, 31, 31, 31, 31, 31, 30, 28, 26, 26, 25,
                               24, 24, 23, 21, 21, 22, 22])
                               [
                                 ('X0', 1), ('X1', 0), ('MC', '101M'),
                                 ('BD', 'JJLLLLKLMKMMMLMLEFFFKJKEEJJKEEJJLFFEEKLKJKMLKKKLKEJKKJIFFJJEJJLJJJJKKLKLMKKLKLKJGGEGLMGKJLMKJJJIHJKJJ'),
                                 ('MD', '0T100'), ('PG', 'MarkDuplicates'), ('RG', 'bwa'), ('XG', 0),
                                 ('BI', 'GGJHKJKJFILKLJKJBBBBEJIBBEJIBBEJJKIBBHJKIJIKIDJHIBILIIG@AIHADIHKLHJKKHIKIKLIIHJHAAJKJJJIJIEDEFEFHKHIK'),
                                 ('AM', 37), ('NM', 1), ('SM', 37), ('XM', 1), ('XO', 0), ('MQ', 60), ('XT', 'U')
                               ]
                               95	0	15712160	0	0	0	0


    """

    # @TODO: Allow adjusting pramaters
    # Number of sites allowed for non-editign
    # min sample coverage - must have been detected in n samples.



    parser.add_argument('-g', "--groups",
                        type=str,
                        default=False,
                        help='')

    parser.add_argument('-v', "--vcf",
                        nargs='*',
                        type=str,
                        required=True,
                        help='')

    parser.add_argument('-b', "--bam",
                        nargs='*',
                        type=str,
                        required=True,
                        help='')

    args = parser.parse_args()

    from lib.parsers import GenomicIntervalTree
    from lib.parsers import VCFIntervalTree
    from lib.parsers import get_coverage
    from pysam import AlignmentFile

    # 1. Make a unique set of all sites.
    # 2. For each site label as undetermineable, non-diff, or differentialble

    vcf_groups = args.vcf
    bam_groups = args.bam

    if args.groups:
        group_labels_set = args.groups.split(",")
    else:
        group_labels_set = [str(i) for i in range(len(vcf_groups))]

    assert len(group_labels_set) == len(vcf_groups)

    group_file_tuples = [(group_labels_set[i], vcf_groups[i], bam_groups[i]) for i in range(len(group_labels_set))]

    # site -> group -> sample
    vcf_set = set()  # {group: dict() for group in group_labels_set}
    vcf_list = []

    bam_group_dict = {}

    for group_name, vcf_group, bam_group in group_file_tuples:

        bam_group_dict.update({group_name: []})
        for bam_file_name in bam_group.split(FILE_DELIMITER):
            bam_group_dict[group_name].append([bam_file_name, AlignmentFile(bam_file_name, "rb")])

        for vcf_file_name in vcf_group.split(FILE_DELIMITER):
            print(vcf_file_name)
            for chrom, pos, id, ref, alt, qual, fil, info in generate_snvs(vcf_file_name):
                # strand = "+" if ref == "A" else "-"
                site_key = (chrom, int(pos), ref, alt)
                vcf_set.add(site_key)
                vcf_list.append(site_key)
                # print(site_key)
                # try:
                #    vcf_dict[site_key][vcf_group].append()
                # except KeyError:
                #    vcf_dict[site_key] = {group: dict() for group in group_labels_set}
                # transition_tuple = (ref, alt)
                # chromosome, position, reference, alteration, sample_name
                # coverage = get_coverage(info)
                # sub = (ref, alt)
                # data = (vcf_file_name, sub, coverage)
                # vcf_it_obj.add_snv(strand, chrom, int(pos), data)
    cutoff = 11

    for site in sorted(vcf_set):
        chrom, pos, ref, alt = site

        group_dict = {}
        for group in sorted(bam_group_dict):

            if group not in group_dict:
                group_dict[group] = {}

            for bam_name, bam_obj in bam_group_dict[group]:
                if bam_name not in group_dict[group]:
                    # print(bam_name)
                    group_dict[group][bam_name] = []

                for read in bam_obj.fetch(chrom, pos, pos + 1):
                    try:
                        not_edited = ref == read.seq[pos - read.pos]
                        group_dict[group][bam_name].append(not_edited)
                        #print(pos, read.pos, pos - read.pos)
                    except IndexError:
                        #print()
                        #print(bam_name, chrom, pos, read.pos, pos - read.pos)
                        pass

        groups = sorted(group_dict)
        groups_len = len(group_dict)
        for g1 in range(1, groups_len):
            for g2 in range(groups_len-1):
                group1 = groups[g1]
                group2 = groups[g2]

                group_1_editing_counts = []
                group_1_coverage = []
                group_1_passing_coverage = 0
                for replicate_name in group_dict[group1]:
                    replicate = group_dict[group1][replicate_name]
                    coverage = len(replicate)
                    group_1_coverage.append(coverage)
                    group_1_editing_counts.append(replicate.count(False))
                    if coverage > cutoff:
                        group_1_passing_coverage += 1

                group_2_editing_counts = []
                group_2_coverage = []
                group_2_passing_coverage = 0
                for replicate_name in group_dict[group2]:
                    replicate = group_dict[group2][replicate_name]
                    coverage = len(replicate)
                    group_2_coverage.append(coverage)
                    group_2_editing_counts.append(replicate.count(False))
                    if coverage > cutoff:
                        group_2_passing_coverage += 1

                # print(group_dict[group1], group_dict[group2])
                # print(group_1_passing_coverage, len(group_dict[group1]), group_2_passing_coverage, len(group_dict[group2]))

                if group_1_passing_coverage > len(group_dict[group1])/2 and group_2_passing_coverage > len(group_dict[group2])/2:

                    try:
                        average_editing_group_1 = round(sum(group_1_editing_counts) / float(len(group_1_editing_counts)), 2)
                    except ZeroDivisionError:
                        average_editing_group_1 = 0

                    try:
                        average_editing_group_2 = round(sum(group_2_editing_counts) / float(len(group_2_editing_counts)), 2)
                    except ZeroDivisionError:
                        average_editing_group_2 = 0

                    # print(average_editing_group_1, average_editing_group_2)
                    if average_editing_group_1 * 0.15 > average_editing_group_2:
                        print(chrom, pos, ref, alt, group1, average_editing_group_1, average_editing_group_2)
                        pass
                    elif average_editing_group_2*0.55 > average_editing_group_1:
                        print(chrom, pos, ref, alt, group2, average_editing_group_1, average_editing_group_2)
                        pass








