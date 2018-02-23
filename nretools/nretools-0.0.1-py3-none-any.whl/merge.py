from lib.parsers import generate_snvs


def merge_editing_sites(parser):
    """ Merges sets of editing sites from multiple studies.
    """

    parser.add_argument(
        "vcf",
        nargs='*',
        type=str,
        help='Two or more VCf files.'
    )

    args = parser.parse_args()

    unique_dict = {}

    for vcf_file in args.vcf:
        for chrom, pos, id, ref, alt, qual, fil, info in generate_snvs(vcf_file):
            site_key = (chrom, pos, ref, alt)
            try:
                unique_dict[site_key] += 1
            except KeyError:
                unique_dict[site_key] = 1

    for dict_key in unique_dict:
        chrom, pos, ref, alt = dict_key
        id, qual, fil, info = ".", ",", ",", str(unique_dict[dict_key])

        print("\t".join([chrom, pos, id, ref, alt, qual, fil, info]))


def find_islands(parser):
    """ Cluster nearby editing sites into editing islands

    :return:
    """

    from sklearn.cluster import DBSCAN

    parser.add_argument('vcf',
                        nargs='*',
                        help='Matrices to add to a base matrix.')

    parser.add_argument('--print-stats',
                        action="store_true",
                        help="")

    parser.add_argument('--epsilon',
                        type=float,
                        default=50,
                        help='Maximum distance between two samples to be labeled as in the same neighborhood.')

    parser.add_argument('--min-samples',
                        type=int,
                        default=5,
                        help='Minimum number of samples needed for a neighborhood to be considered as a core point.')

    args = parser.parse_args()

    # from lib.parsers import get_coverage
    from hashlib import md5
    import base64

    # Sort by chromosome, what about strand?
    chromosome_dict = {"+": {}, "-": {}}
    chromosome_set = set()

    for vcf_file_name in args.vcf:
        for chrom, pos, id, ref, alt, qual, fil, info in generate_snvs(vcf_file_name):

            strand = "+" if ref == "A" else "-"

            p = [int(pos)]
            chromosome_set.add(chrom)
            try:
                chromosome_dict[strand][chrom].append(p)
            except KeyError:
                chromosome_dict[strand].update({chrom: [p]})

            # sub = (ref, alt)
            # coverage = get_coverage(info)
            # data = (vcf_file_name, sub, coverage)
            # vcf_it_obj.add_snv(strand, chrom, int(pos), data)

    for strand in chromosome_dict:
        for chromosome in chromosome_dict[strand]:

            pos_list = chromosome_dict[strand][chromosome]
            l = len(pos_list)
            db = DBSCAN(eps=args.epsilon, min_samples=args.min_samples).fit(pos_list)

            # Make lists of bounds
            island_dict = {}
            for i in range(l):
                try:
                    island_dict[db.labels_[i]].append(pos_list[i])
                except KeyError:
                    island_dict[db.labels_[i]] = [pos_list[i]]

            for label in range(len(island_dict) - 1):
                z = sorted(island_dict[label])
                b1 = z[0][0]
                b2 = z[-1][0]+1
                h = "%s%s%s-%s" % (chromosome, strand, b1, b2)
                md5_digest = base64.urlsafe_b64encode(md5(h.encode('utf-8')).digest())[:-2].decode('ascii')

                # print-stats
                if args.print_stats:
                    print("\t".join([
                        chromosome, str(b1), str(b2),
                        md5_digest, "0", strand,
                        str(b2 - b1),  # length of island
                        str(len(z)),     # number of sites in island
                        str(len(z)/float(b2 - b1))
                    ]))
                else:
                    print("\t".join([chromosome, str(b1), str(b2), md5_digest, str(b2-b1), strand]))


def merge_editing_islands(parser):
    """ Merge editing islands
    """
    pass


