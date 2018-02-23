# from intervaltree import Interval, IntervalTree
from lib.parsers import generate_snvs
from lib.io import _shared_params
import numpy as np


def find_total_area_covered(n, file_name):
    total_area = 0
    for line in open(file_name):
        sl = line.split()
        if sl[0] == "genome" and int(sl[1]) >= n:
            total_area += int(sl[2])
    return total_area


def normalized_editing(sites, total_area_covered):
    return round((sites * 1.0e6) / total_area_covered, 5)


def find_coverage(info):
    return int(info.split("DP=")[-1].split(";")[0])


class DataStore:

    def __init__(self, count):
        pass


def sample(parser):
    """ Return various data regarding overall-editing in one or more samples.

    1. Total editing sites
    2. Basic SNV counts
    3. If given bam file or coverage file, give EPKM
    4. If given editing island bed file, Adar1 and Adar2 editing profiles, if bam or coverge file give EPKM
    5. If GTF given then calculate in which regions the editing sites fall, if editing island file given then
        calculate Adar1 and Adar2 types too.

    Misc flags
    - Enforce cutoff of N
    - Ignore Adar1 sites
    - Ignore Adar2 sites

    hekase sample --gtf   Homo_sapiens.GRCh38.90.gtf                   \\
                  --names SRR2087305,SRR1998058,SRR2087291             \\
                  --vcf   SRR2087305.vcf,SRR1998058.vcf,SRR2087291.vcf \\
                  --bam   SRR2087305,SRR1998058,SRR2087291
    """

    _shared_params(parser)

    args = parser.parse_args()

    from lib.parsers import GenomicIntervalTree, BedIntervalTree

    # =========================
    # Set up data structures
    # =========================
    vcf_list = args.vcf

    # First we need to know if we will be differentiating between Adar1 and Adar2 sites
    if args.editing_islands:
        # Create an interval tree from editing islands and use it to discriminate Adar1 from Adar2 sites.
        island_interval_tree = BedIntervalTree()
        island_interval_tree.add_islands_from_file(args.editing_islands)

    # Base output columns.
    titles = ["Sample", "ESs"]

    """
    if args.coverage:
        coverage_list = args.coverage
        titles.append("NESs")
        # if args.editing_islands:
        #    titles.append("A1_" + "NESs")
        #    titles.append("A2_" + "NESs")
    """

    coverage_list = []
    if args.coverage:
        coverage_list = args.coverage
        titles.append("EPKM")

    # Generate data structures for Base counting.
    bases = ["A", "C", "G", "T"]
    transition_tuple_list = []
    transition_tuple_titles = []
    # Make all unique transitions
    for b1 in bases:
        for b2 in bases:
            if b1 != b2:
                transition_tuple_list.append((b1, b2))
                transition_tuple_titles.append("%s>%s" % (b1, b2))
                transition_dict = {t: 0 for t in transition_tuple_list}

    titles += transition_tuple_titles  # A>C A>G ...
    # If discriminate Adar1 from Adar2 we need additional columns
    if args.editing_islands:
        titles += ["A1_" + title for title in transition_tuple_titles]  # A>C A>G ...
        titles += ["A2_" + title for title in transition_tuple_titles]  # A>C A>G ...

    names_dict = {}
    if args.names:
        names_list = args.names.split(",")
        assert len(names_list) == len(vcf_list)
        # For finding aliases given by names flag.
        for i in range(len(names_list)):
            names_dict[vcf_list[i]] = names_list[i]

    if args.gtf:
        gtf = args.gtf
        # Initialize variables for various columns.
        # Build interval tree for fast position searches. This can take some time so report to users.
        # print("Generating interval tree ......", end=" ",  flush=True)
        interval_tree = GenomicIntervalTree(gtf)
        genomic_features = interval_tree.genomic_features

    if args.gtf:
        ge_title = ["ES_" + s for s in genomic_features]
        titles += ge_title
        if args.editing_islands:
            titles += ["A1_" + title for title in ge_title]
            titles += ["A2_" + title for title in ge_title]

    # Make variables for holding row information.
    if args.gtf:
        features_dict = {t: 0 for t in genomic_features}

    """
    if args.gtf and args.coverage:
        # norm_ge_titles = ["NES_" + s for s in genomic_features]
        #titles += norm_ge_titles
        if args.editing_islands:
            titles += ["A1_" + title for title in norm_ge_titles]
            titles += ["A2_" + title for title in norm_ge_titles]
    """

    # First print the titles.
    print("\t".join(titles))
    # Count total area of features
    # Run name check i.e. name should have unique intersect greater than other names with paired values.
    # Build collection of editing sites.

    for i in range(len(vcf_list)):

        vcf_file = vcf_list[i]
        # Make variables for holding row information.
        if args.gtf:
            features_dict = {t: 0 for t in genomic_features}
            if args.editing_islands:
                adar1_features_dict = {t: 0 for t in genomic_features}
                adar2_features_dict = {t: 0 for t in genomic_features}

        tmp_transition_dict = {t: 0 for t in transition_tuple_list}
        if args.editing_islands:
            tmp_adar1_transition_dict = {t: 0 for t in transition_tuple_list}
            tmp_adar2_transition_dict = {t: 0 for t in transition_tuple_list}

        snv_dict = {}

        name = vcf_file
        if args.names:
            name = names_dict[vcf_file]

        total_area_covered = None
        if args.coverage:
            total_area_covered = find_total_area_covered(args.min_site_coverage, coverage_list[i])

        for chrom, pos, id, ref, alt, qual, fil, info in generate_snvs(vcf_file):
            # Find coverage
            site_coverage = find_coverage(info)
            if site_coverage >= args.min_site_coverage:
                strand = "+" if ref == "A" else "-"
                site_key = (chrom, pos, ref, alt)
                transition_tuple = (ref, alt)

                # Count occurrences in locations
                # First find overlapping genes.
                if args.gtf:
                    gene_set_list = interval_tree.get_genes_overlapping_position(chrom, int(pos), strand)
                    if gene_set_list:
                        overlapping_spliced_features = interval_tree.get_spliced_features_overlapping_position(chrom, int(pos), strand)
                        if overlapping_spliced_features:
                            for f in overlapping_spliced_features:
                                for tmp_tuple in f[-1]:
                                    tmp_feature_type = tmp_tuple[0]
                                    try:
                                        features_dict[tmp_feature_type] += 1
                                        if island_interval_tree.location_is_in_interval(chrom, int(pos)):
                                            adar1_features_dict[tmp_feature_type] += 1
                                        else:
                                            adar2_features_dict[tmp_feature_type] += 1
                                    except KeyError:
                                        features_dict.update({tmp_feature_type: 1})
                        else:
                            # Intronic
                            features_dict["intron"] += 1
                            if island_interval_tree.location_is_in_interval(chrom, int(pos)):
                                adar1_features_dict["intron"] += 1
                            else:
                                adar2_features_dict["intron"] += 1
                    else:
                        features_dict["intergenic"] += 1
                        if island_interval_tree.location_is_in_interval(chrom, int(pos)):
                            adar1_features_dict["intergenic"] += 1
                        else:
                            adar2_features_dict["intergenic"] += 1

                # Count transitions
                try:
                    tmp_transition_dict[transition_tuple] += 1
                    if args.editing_islands:
                        if island_interval_tree.location_is_in_interval(chrom, int(pos)):
                            tmp_adar1_transition_dict[transition_tuple] += 1
                        else:
                            tmp_adar2_transition_dict[transition_tuple] += 1
                except KeyError:
                    print("Warning: Bases %s and/or %s not included in base dict." % transition_tuple)

                try:
                    snv_dict[site_key].add(name)
                except KeyError:
                    snv_dict[site_key] = set(name)

        # Number of sites
        # for name in names_list:
        total_sites = len(snv_dict)

        out_list = [name, str(len(snv_dict))]

        if args.coverage:
            normalized_site_count = normalized_editing(total_sites, total_area_covered)
            out_list += [str(normalized_site_count)]

        out_list += [str(tmp_transition_dict[i]) for i in transition_tuple_list]
        if args.editing_islands:
            out_list += [str(tmp_adar1_transition_dict[i]) for i in transition_tuple_list]
            out_list += [str(tmp_adar2_transition_dict[i]) for i in transition_tuple_list]

        if args.gtf:
            out_list += [str(features_dict[i]) for i in genomic_features]
            if args.editing_islands:
                out_list += [str(adar1_features_dict[i]) for i in genomic_features]
                out_list += [str(adar2_features_dict[i]) for i in genomic_features]

        print("\t".join(out_list))


def genomic_region(parser):
    """ Return various data regarding the genes in one or more samples.

    """

    _shared_params(parser)

    print_zero_genes = False

    args = parser.parse_args()

    from lib.parsers import VCFIntervalTree
    from lib.parsers import get_coverage

    # Make interval tree of vcf locations
    vcf_it_obj = VCFIntervalTree()

    # Build interval tree from all VCF files.
    for vcf_file_name in args.vcf:
        for chrom, pos, id, ref, alt, qual, fil, info in generate_snvs(vcf_file_name):
            strand = "+" if ref == "A" else "-"
            # site_key = (chrom, pos, ref, alt)
            # transition_tuple = (ref, alt)
            # chromosome, position, reference, alteration, sample_name
            coverage = get_coverage(info)
            sub = (ref, alt)
            data = (vcf_file_name, sub, coverage)
            vcf_it_obj.add_snv(strand, chrom, int(pos), data)

    # For gene in GTf file find overlapping
    from lib.parsers import GFF
    gff_obj = GFF(args.gtf)

    print(
        "gene_id",
        "gene_name",
        "gene_len",
        "unique_editing_sites",
        "total_observed_sites_in_all_samples",
        "Ratio_of_Unique_to_Total_Sites",
        "Unique_sites_divided_by_gene_len",
        "Editing_Ratio_3",
        "avg_depth",
        "avg_percent_edited_list"
    )

    # Record is a line in a GFF or GTF file.
    for record in gff_obj.yield_lines():

        if record.feature == "gene":

            # Get all SNVs falling within gene.
            try:
                v = vcf_it_obj.get_snvs_within_range(record.chromosome, record.strand, record.start, record.end)
            except KeyError:
                # print("Chromosome not found.", record.chromosome, record.strand, record.start, record.end)
                v = {}

            total_observed_sites_in_all_samples = len(v)

            if total_observed_sites_in_all_samples > 1:

                s_dict = {}

                base_cnt = 0
                avg_depth_list = []
                avg_percent_edited_list = []

                for s in sorted(v):
                    base_cnt += 1
                    pos = "%s-%s" % (s[0], s[1])
                    depth = float(s[-1][-1][-1])
                    number_of_edited_reads = float(s[-1][-1][0])
                    percentage = number_of_edited_reads/depth

                    try:
                        s_dict[pos] += 1
                    except KeyError:
                        s_dict[pos] = 1

                    avg_depth_list.append(depth)
                    avg_percent_edited_list.append(percentage)

                avg_depth = round(np.mean(avg_depth_list), 4)
                avg_percent_edited_list = round(np.mean(avg_percent_edited_list), 4)
                unique_editing_sites = len(s_dict)

                gene_len = record.end - record.start

                gene_denominator = float(gene_len) / 1.0e6

                out_list = [
                    record.gene_id,
                    record.gene_name,
                    gene_len,
                    unique_editing_sites,
                    total_observed_sites_in_all_samples,
                    round(float(unique_editing_sites)/float(total_observed_sites_in_all_samples), 1),
                    round(unique_editing_sites/gene_denominator, 5),
                    round(total_observed_sites_in_all_samples/gene_denominator, 5),
                    avg_depth,
                    avg_percent_edited_list
                    ]

                print("\t".join([str(s) for s in out_list]))


def editing_site(parser):
    """ Calculate stats for individual editing sites.

    :param parser:
    :return:
    """
    _shared_params(parser)

    args = parser.parse_args()

    from statistics import mean, variance, stdev

    from lib.parsers import GenomicIntervalTree, BedIntervalTree

    titles = [
        "#chrom",
        "pos",
        "id",
        "ref",
        "alt",
        "detections",
        "dropouts",
        "average_depth"
        "variance",
        "stdev"
    ]

    if args.gtf:
        gtf = args.gtf
        # Initialize variables for various columns.
        # Build interval tree for fast position searches. This can take some time so report to users.
        # print("Generating interval tree ......", end=" ",  flush=True)
        interval_tree = GenomicIntervalTree(gtf)
        genomic_features = interval_tree.genomic_features
        titles += [i for i in sorted(genomic_features)]

    # Should we differentiate between Adar1 and Adar2 sites
    island_interval_tree = None
    if args.editing_islands:
        # Create an interval tree from editing islands and use it to discriminate Adar1 from Adar2 sites.
        island_interval_tree = BedIntervalTree()
        island_interval_tree.add_islands_from_file(args.editing_islands)
        titles.append("Adar")

    vcf_dict = {}

    number_of_vcf_files = len(args.vcf)

    for vcf_file in args.vcf:
        for chrom, pos, id, ref, alt, qual, fil, info in generate_snvs(vcf_file):
            metadata = []
            tmp_site_tuple = (chrom, pos, id, ref, alt)
            depth = int(info.split("DP=")[-1].split(";")[0])
            strand = "+" if ref == "A" else "-"
            features_dict = {t: "0" for t in genomic_features}

            if args.gtf:
                gene_set_list = interval_tree.get_genes_overlapping_position(chrom, int(pos), strand)
                if gene_set_list:
                    overlapping_spliced_features = interval_tree.get_spliced_features_overlapping_position(
                        chrom, int(pos), strand)

                    if overlapping_spliced_features:
                        for f in overlapping_spliced_features:
                            for tmp_tuple in f[-1]:
                                tmp_feature_type = tmp_tuple[0]
                                try:
                                    features_dict[tmp_feature_type] = "1"
                                except KeyError:
                                    features_dict.update({tmp_feature_type: "1"})
                    else:
                        features_dict["intron"] = "1"
                else:
                    features_dict["intergenic"] = "1"

                metadata = [features_dict[i] for i in features_dict]

            try:
                vcf_dict[tmp_site_tuple][0].append(depth)
            except KeyError:
                vcf_dict[tmp_site_tuple] = [[depth], metadata]

    print("\t".join(titles))

    for site_tuple in sorted(vcf_dict):

        site_location = "\t".join(site_tuple)
        site_data = vcf_dict[site_tuple][0]
        detections = len(site_data)

        new_data = [
            str(detections),                        # Number of samples with editing site.
            str(number_of_vcf_files - detections),  # Drop out events
            str(round(mean(site_data), 2)),
            str(round(variance(site_data), 2)) if detections > 1 else "0",
            str(round(stdev(site_data), 2)) if detections > 1 else "0",
        ]

        if args.gtf:
            new_data += vcf_dict[site_tuple][-1]

        if args.editing_islands:
            if island_interval_tree.location_is_in_interval(site_tuple[0], int(site_tuple[1])):
                adar = "A1"
            else:
                adar = "A2"
            new_data.append(adar)

        # Find some feature info if GTF file is passed.
        # Classify as ADAR1 or ADAR2 if island passed.
        print(site_location+"\t"+"\t".join(new_data))




def annotate_regions(parser):
    """ Annotate a given bed file with average per base coverage, %of each base pair,

    length, average_coverage, stddev_average_coverage, %A, %c, %T, %G

    [Interval(42886256, 42889896, {('exon', 'ENSG00000146223', 'ENST00000493763', 'ENSE00001934591')}),
    Interval(42886465, 42889896, {('three_prime_utr', 'ENSG00000146223', 'ENST00000493763', '+6:42886465-42889896')}),
    Interval(42887160, 42889925, {('three_prime_utr', 'ENSG00000146223', 'ENST00000304734', '+6:42887160-42889925'),
    ('exon', 'ENSG00000146223', 'ENST00000304734', 'ENSE00001175322')})]

    e90_human_alu_repeats.bed
    :param parser:
    :return:
    """

    parser.add_argument('bed',
                        help='Bed file containing regions to annotate.')

    parser.add_argument('--gtf',
                        help='A gtf file containing genomic annotations.')

    parser.add_argument('--genome',
                        help='A fasta file containing a genome.')

    parser.add_argument("--alignment", type=str, required=True, help='')

    # parser.add_argument('-v', "--vcf", nargs='*', type=str, required=True, help='')

    args = parser.parse_args()

    from pysam import Fastafile
    from pysam import AlignmentFile
    from lib.parsers import GenomicIntervalTree
    from statistics import mean, stdev
    from lib.parsers import yield_bed_lines
    # Build feature Interval Tree

    reference_genome = None
    if args.genome:
        reference_genome = Fastafile(args.genome)

    aligned_reads = None
    if args.alignment:
        aligned_reads = AlignmentFile(args.alignment, "rb")

    genome_features_interval_tree = None
    if args.gtf:
        # Make feature Interval Tree
        genome_features_interval_tree = GenomicIntervalTree(args.gtf)

    for bed_el in yield_bed_lines(args.bed):

        out_list = [bed_el.chromosome, str(bed_el.start), str(bed_el.end), bed_el.name, bed_el.score, bed_el.strand]
        if args.genome:
            sequence = reference_genome.fetch(bed_el.chromosome, bed_el.start, bed_el.end)
            seq_len = len(sequence)
            seq_len_float = float(seq_len)
            out_list.append(str(seq_len))
            out_list.append(str(round(sequence.count("A") / seq_len_float, 3)))
            out_list.append(str(round(sequence.count("C") / seq_len_float, 3)))
            out_list.append(str(round(sequence.count("G") / seq_len_float, 3)))
            out_list.append(str(round(sequence.count("T") / seq_len_float, 3)))

        if args.alignment:
            average_coverage = []
            for pos in range(bed_el.start, bed_el.end):
                tmp_base_list = []
                for read in aligned_reads.fetch(bed_el.chromosome, pos, pos + 1):
                    # not_edited = ref == read.seq[pos - read.pos]
                    try:
                        tmp_base_list.append(read.seq[pos - read.pos])
                    except IndexError:
                        pass

                average_coverage.append(len(tmp_base_list))

            out_list.append(str(round(mean(average_coverage), 2)))
            out_list.append(str(round(stdev(average_coverage), 2)))

        if args.gtf:
            overlapping_features = genome_features_interval_tree.get_spliced_features_overlapping_range(
                bed_el.chromosome, bed_el.start, bed_el.end, bed_el.strand)
            feature_set = set()
            for interval_obj in overlapping_features:
                for f in interval_obj[-1]:
                    feature_set.add(f[0])
            feature_str = ";".join(sorted(list(feature_set)))
            out_list.append(feature_str)

        print("\t".join(out_list))

