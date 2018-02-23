from lib.parsers import generate_snvs


def find_total_area_covered(n, file_name):
    total_area = 0
    for line in open(file_name):
        sl = line.split()
        if int(sl[1]) >= n:
            total_area += int(sl[2])
    return total_area


def calculate_EPMCBP(parser):
    """
    chromosome  depth   bps_covered_by  percent
    1	0	218256120	248956422	0.876684
    1	1	9532255	248956422	0.0382889
    1	2	4797353	248956422	0.0192699
    1	3	2582708	248956422	0.0103741



    :return:
    """
    parser.add_argument("--coverage",
                        type=str,
                        required=True,
                        help='')

    parser.add_argument("--vcf",
                        type=str,
                        required=True,
                        help='')

    args = parser.parse_args()

    editing_sites = 0
    with open(args.vcf) as vcf_file:
        for line in vcf_file:
            editing_sites += 1

    coverage_dict = {}
    with open(args.coverage) as coverage_file:
        for line in coverage_file:
            sl = line.split()


def normalized_editing(sites, total_area_covered):
    return round((sites * 1.0e6) / total_area_covered, 5)


def calculate_EPCMRGN(parser):
    """ Calculate EPCMBGN - Editing Per Megabase of Mapped Reads with coverage Greater than N.

    samtools view -b {input} | genomeCoverageBed -ibam stdin -g {params.genome} > {output}

    hekase sample --gtf   Homo_sapiens.GRCh38.90.gtf                   \
                  --names SRR2087305,SRR1998058,SRR2087291             \
                  --vcf   SRR2087305.vcf,SRR1998058.vcf,SRR2087291.vcf \
                  --bam   SRR2087305,SRR1998058,SRR2087291

    parser.add_argument("--bam",
                        required=False,
                        help='')

    """

    parser.add_argument("--vcf",
                        type=str,
                        required=True,
                        help='')

    parser.add_argument("--coverage",
                        required=False,
                        help='')

    # Count number of editing sites.
    args = parser.parse_args()

    editing_site_counts = 0
    for chrom, pos, id, ref, alt, qual, fil, info in generate_snvs(args.vcf):
        editing_site_counts += 1

    coverage_dict = {}
    total = 0
    with open(args.coverage) as coverage_file:
        for line in coverage_file:
            sl = line.split()
            if sl[0] != "genome" and int(sl[1]) > 0:
                total += int(sl[2])

    if args.coverage:  # sites, total_area_covered
        normalized_site_count = normalized_editing(editing_site_counts, total)

    print(editing_site_counts, total, normalized_site_count)


def sample(parser):
    """ Return various data regarding overall-editing in one or more samples.

    chromosome  depth   bps_covered_by  percent
    1	0	218256120	248956422	0.876684
    1	1	9532255	248956422	0.0382889
    1	2	4797353	248956422	0.0192699
    1	3	2582708	248956422	0.0103741


    hekase sample --gtf   Homo_sapiens.GRCh38.90.gtf                   \
                  --names SRR2087305,SRR1998058,SRR2087291             \
                  --vcf   SRR2087305.vcf,SRR1998058.vcf,SRR2087291.vcf \
                  --bam   SRR2087305,SRR1998058,SRR2087291
    """
    '''

    parser.add_argument('-n', "--names",
                        type=str,
                        required=True,
                        help='')
    '''
    parser.add_argument('-c', "--coverage",
                        nargs='*',
                        type=str,
                        required=True,
                        help='')

    parser.add_argument('-v', "--vcf",
                        nargs='*',
                        type=str,
                        required=True,
                        help='')
    '''
    parser.add_argument('-b', "--bam",
                        type=str,
                        required=True,
                        help='')
    '''

    args = parser.parse_args()

    data_set_site = len(args.coverage)
    assert data_set_site == len(args.vcf)

    import numpy as np
    min_coverage = 0
    max_coverage = 40

    coverage_list = []
    for coverage_file_name in args.coverage:
        coverage_area_dict = {}
        with open(coverage_file_name) as coverage_file:

            for line in coverage_file:

                sl = line.split()
                coverage_level = int(sl[1])

                if sl[0] != "genome" and coverage_level > min_coverage:

                    area_coverage = int(sl[2])

                    if coverage_level > max_coverage:
                        coverage_level = max_coverage

                    try:
                        coverage_area_dict[coverage_level] += area_coverage
                    except KeyError:
                        coverage_area_dict[coverage_level] = area_coverage

        coverage_list.append(coverage_area_dict)

    from statistics import variance, mean, stdev
    site_depth_list = []
    for vcf_file_name in args.vcf:
        vcf_cov_dict = {}
        for line in open(vcf_file_name):
            coverage_level = int(line.split("DP=")[-1].split(";")[0])
            if coverage_level > max_coverage:
                coverage_level = max_coverage
            try:
                vcf_cov_dict[coverage_level] += 1
            except KeyError:
                vcf_cov_dict[coverage_level] = 1

        site_depth_list.append(vcf_cov_dict)

    rescaled_editing_counts = [0 for _ in range(data_set_site)]
    rescaled_coverage = 0
    coverage_cnt = [0 for _ in range(data_set_site)]
    vcf_cnt = [0 for _ in range(data_set_site)]
    for i in range(1, max_coverage):
        # Standard score.
        # (Value - Mean)/ Variance
        # Get read coverage
        try:
            total_bases_coverage = [float(cov_dict[i]) for cov_dict in coverage_list]
        except:
            print("!!!!")
            for q in coverage_list:
                print(list(q))
            #print(list(coverage_list))

        try:
            total_editing = [float(vcf_dict[i]) for vcf_dict in site_depth_list]
        except:
            print("???")
            for q in site_depth_list:
                print(list(q))

        average_cov = mean(total_bases_coverage)
        rescaled_coverage += average_cov
        # Find scaling factors
        for j in range(len(total_bases_coverage)):
            scaling_factor = average_cov/total_bases_coverage[j]
            rescaled_editing_counts[j] += scaling_factor * total_editing[j]
            # rescaled_coverage[j] += average_cov
            coverage_cnt[j] += total_bases_coverage[j]
            vcf_cnt[j] += total_editing[j]

    # Print normalized EPM
    for i in range(data_set_site):
        print(
            args.coverage[i],
            round(rescaled_editing_counts[i]),
            round(rescaled_coverage),
            round(coverage_cnt[i]),
            round(vcf_cnt[i])
        )

    print(stdev(vcf_cnt))
    print(stdev(rescaled_editing_counts))


def genomic_region(parser):
    """ Normalize editing rates among genomic regions.

    :param parser:
    :return:
    """
    pass


def editing_site(parser):
    """ Normalize editing by sites.

    :param parser:
    :return:
    """
    pass