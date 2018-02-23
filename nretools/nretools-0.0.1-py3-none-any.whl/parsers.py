from intervaltree import IntervalTree

comments_and_title_char = "#"


def yield_bed_lines(bed_file):
    from collections import namedtuple

    # "source", "feature",

    bed_record = namedtuple('GFFRecord', [
        "chromosome",
        "start",
        "end",
        "name",
        "score",
        "strand"
    ])

    with open(bed_file) as bed_file_obj:

        for line in bed_file_obj:

            sl = line.split()

            chromosome = sl[0]
            start = int(sl[1])
            end = int(sl[2])

            try:
                name = sl[3]
            except IndexError:
                name = "."

            try:
                score = sl[4]
            except IndexError:
                score = "."

            try:
                strand = sl[5]
            except IndexError:
                strand = "."

            yield bed_record(chromosome, start, end, name, score, strand)


class GroupsManager:

    def __init__(self):
        pass

    def add_vcf_groups(self, input_string):
        # Check if other groups have been added
        pass

    def add_bam_groups(self, input_string):
        pass

    def find_group_of_file(self, file_name):
        pass


def get_coverage(info):
    # 1       100146605       .       A       G       6.79    .
    # ABHet=0.769;AC=1;AF=0.500;AN=2;BaseQRankSum=-0.849;
    # DP=14;
    # Dels=0.00;ExcessHet=3.0103;FS=0.000;
    # HaplotypeScore=3.3240;MLEAC=1;MLEAF=0.500;MQ=54.03;MQ0=0;MQRankSum=1.146;OND=0.00;QD=0.52;
    # ReadPosRankSum=0.681;SOR=1.179   GT:AD:DP:GQ:PL
    # 0/1:10,3:14:34:34,0,254  --> 0/1:10,  3:14:34:34  ,0,254
    # A, C, G, T = info.split("BaseCounts=")[-1].split(";")[0].split(",")  # 1,0,2,0
    # return int(A), int(C), int(G), int(T)
    # mod_cnt = info.split("DP=")[-1].split(";")[0]
    # ref_cnt = info.split("BaseCounts=")[-1].split(";")[0].split(",")
    ref, alt = info.split()[-1].split(",")[1].split(":")[:2]

    return ref, alt


#class BedParser:
#    def __init__(self, bed_file):


class GFF:

    def __init__(self, gff_file, attribute_format="Ensembl"):

        from collections import namedtuple
        self.file_location = gff_file
        self.attribute_format = attribute_format
        # @TODO: Add more formats and use UGAs if no reference not supported.
        if attribute_format == "Ensembl":
            self.gene_id_regex = 'gene_id "'
            self.gene_name_regex = 'gene_name "'
            self.tran_id_regex = 'transcript_id "'
            self.exon_id_regex = 'exon_id "'
        else:
            self.gene_id_regex = 'gene_id "'
            self.gene_name_regex = 'gene_name "'
            self.tran_id_regex = 'transcript_id "'
            self.exon_id_regex = 'exon_id "'
        # "frame", "attribute",
        GFFRecord = namedtuple('GFFRecord', [
            "chromosome", "source", "feature", "start", "end", "strand",
            "gene_id", "gene_name", "tran_id", "exon_id"
        ])
        self.GFFRecord = GFFRecord

    def yield_lines(self):
        with open(self.file_location) as gff_obj:
            for line in gff_obj:
                if line[0] != "#":
                    sl = line.split()
                    chromosome = sl[0]
                    source = sl[1]
                    feature = sl[2]
                    start = int(sl[3])
                    end = int(sl[4])
                    strand = sl[6]
                    # frame = sl[5 or 7?]
                    attribute = " ".join(sl[6:])

                    gene_id = self.get_gene_id(attribute)
                    gene_name = self.get_gene_name(attribute)

                    tran_id = self.get_transcript_id(attribute)
                    exon_id = self.get_exon_id(attribute, chromosome, strand, start, end)

                    # Convert to 1 based counts as we will be searching with VCF files.
                    end = end + 1 if start - end == 0 else end

                    yield self.GFFRecord(chromosome, source, feature, start, end, strand, gene_id, gene_name, tran_id, exon_id)

    def get_gene_id(self, attributes):
        return attributes.split(self.gene_id_regex)[-1].split('";')[0] if self.gene_id_regex in attributes else None

    def get_gene_name(self, attributes):
        return attributes.split(self.gene_name_regex)[-1].split('";')[0] if self.gene_name_regex in attributes else None

    def get_transcript_id(self, attributes):
        return attributes.split(self.tran_id_regex)[-1].split('";')[0] if self.tran_id_regex in attributes else None

    def get_exon_id(self, attributes, chromosome, strand, start, end):

        if self.exon_id_regex in attributes:
            return attributes.split(self.exon_id_regex)[-1].split('";')[0]
        else:
            return "%s%s:%s-%s" % (strand, chromosome, start, end)

# gene_coverage_cnt_dict[record.chromosome][record.start:record.end] = None
# for s in self.gene_tree_dict:


class GenomicIntervalTree:
    """

    """

    def __init__(self, gtf_file):

        from intervaltree import IntervalTree, Interval
        # Here we build two tree dictionaries. The purpose of these is so that we can differentiate between
        # between reads falling in exons and those falling in intergenic space. The problem is that intergenic
        # space is not annotated so falling within the bounds of a gene and not an exonic feature
        # Finally we use dictionaries to differentiate between chromosome and strand.
        self.gene_tree_dict = {"+": dict(), "-": dict()}
        self.exon_tree_dict = {"+": dict(), "-": dict()}
        self.total_area_covered_by_genes = 0
        self.total_intergenic_area = 0
        self.total_intronic_are = 0
        self.total_area_covered_by_exons = 0
        self.total_area_covered_by_3utr = 0
        self.total_area_covered_by_5utr = 0
        gene_coverage_cnt_dict = {}
        exonic_feature_bounds_dict = {}

        intergenic = "intergenic"
        exon = "exon"
        intron = "intron"
        three_prime_utr = "three_prime_utr"
        five_prime_utr = "five_prime_utr"

        self.genomic_features = [intergenic, exon, intron, three_prime_utr, five_prime_utr]
        self.exonic_feature_set = {exon, five_prime_utr, three_prime_utr}
        self.feature_set_lens = {k: 0 for k in self.genomic_features}

        unique_exon_lens = []
        unique_five_prime_lens = []
        unique_three_prime_lens = []

        # exonic_feature_set_lens = {f: 0 for f in exonic_feature_bounds_dict}
        # exonic_feature_set_bound_sets = {"exon": set(), "five_prime_utr": set(), "three_prime_utr": set()}
        # exonic_feature_dict = {}
        # exon_set = set()
        # five_prime_utr_set = set()
        # three_prime_utr_set = set()
        gff_obj = GFF(gtf_file)
        # Record is a line in a GFF or GTF file.
        for record in gff_obj.yield_lines():
            if record.chromosome not in self.gene_tree_dict[record.strand]:
                self.gene_tree_dict[record.strand][record.chromosome] = IntervalTree()
                self.exon_tree_dict[record.strand][record.chromosome] = IntervalTree()
                gene_coverage_cnt_dict[record.chromosome] = IntervalTree()

            if record.feature == "gene":
                # self.total_area_covered_by_genes += record.start - record.end
                self.gene_tree_dict[record.strand][record.chromosome][record.start:record.end] = record.gene_id
                gene_coverage_cnt_dict[record.chromosome][record.start:record.end] = None

            elif record.feature in self.exonic_feature_set:
                # Get all unique exonic annotations, exons will occur multiple times unlike genes and transcripts.
                location_tuple = (record.strand, record.chromosome, record.start, record.end)
                annotation = (record.feature, record.gene_id, record.tran_id, record.exon_id)
                try:
                    exonic_feature_bounds_dict[location_tuple].add(annotation)
                except KeyError:
                    # {(annotation,)} Will not work
                    # annotation = (record.feature, record.gene_id, record.tran_id, record.exon_id, "!!!")

                    exonic_feature_bounds_dict[location_tuple] = set()
                    exonic_feature_bounds_dict[location_tuple].add(annotation)

        # Add unique exonic features to dictionary of strand chromosome and interval trees.
        for location_key, annotation_values in exonic_feature_bounds_dict.items():

            location_length = location_key[3] - location_key[2]
            tmp_location_types = set()
            for tmp_annotation in annotation_values:
                # tmp_feature = tmp_annotation[0]
                tmp_location_types.add(tmp_annotation[0])  # tmp_feature
                # print("---", tmp_annotation)
                # exonic_feature_set_lens[tmp_feature] += 1

            if exon in tmp_location_types:
                unique_exon_lens.append(location_length)
            if three_prime_utr in tmp_location_types:
                unique_three_prime_lens.append(location_length)
            if five_prime_utr in tmp_location_types:
                unique_five_prime_lens.append(location_length)

            strand, chromosome, start, end = location_key
            self.exon_tree_dict[strand][chromosome][start:end] = annotation_values

        for c in gene_coverage_cnt_dict:
            gene_coverage_cnt_dict[c].merge_overlaps()
            for o in gene_coverage_cnt_dict[c]:
                self.total_area_covered_by_genes += o[1] - o[0]

        # chr 1 248956422
        self.total_intergenic_area = 3099411205 - self.total_area_covered_by_genes
        self.total_area_covered_by_exons = sum(unique_exon_lens)
        self.total_area_covered_by_3utr = sum(unique_three_prime_lens)
        self.total_area_covered_by_5utr = sum(unique_five_prime_lens)
        intron_area = self.total_area_covered_by_genes - self.total_area_covered_by_exons

        self.feature_set_lens[intergenic] = 248956422 - self.total_area_covered_by_genes
        self.feature_set_lens[exon] = self.total_area_covered_by_exons
        self.feature_set_lens[intron] = intron_area
        self.feature_set_lens[three_prime_utr] = self.total_area_covered_by_3utr
        self.feature_set_lens[five_prime_utr] = self.total_area_covered_by_5utr

    def get_genes_overlapping_position(self, chromosome, position, strand):
        """
        :param chromosome:
        :param position:
        :param strand:
        :return:
        """
        if chromosome in self.gene_tree_dict[strand]:
            return sorted(self.gene_tree_dict[strand][chromosome][position])
        else:
            return []

    def get_spliced_features_overlapping_position(self, chromosome, position, strand):

        if chromosome in self.exon_tree_dict[strand]:
            return sorted(self.exon_tree_dict[strand][chromosome][position])
        else:
            return []

    def get_spliced_features_overlapping_range(self, chromosome, start, end, strand):

        if chromosome in self.exon_tree_dict[strand]:
            return sorted(self.exon_tree_dict[strand][chromosome][start:end])
        else:
            return []

    def get_count_of_overlapping_features(self, chromosome, position, strand):
        pass


class BedIntervalTree:

    def __init__(self):
        self.interval_tree = dict()

    def add_island(self, chromosome, start, end):

        start = int(start)
        end = int(end)

        try:
            self.interval_tree[chromosome][start:end] = True
        except KeyError:
            self.interval_tree[chromosome] = IntervalTree()
            self.interval_tree[chromosome][start:end] = True

    def add_islands_from_file(self, bed_file):
        with open(bed_file) as bed_obj:
            for line in bed_obj:
                sl = line.split()
                chromosome, start, end = sl[0], sl[1], sl[2]
                self.add_island(chromosome, start, end)

    def location_is_in_interval(self, chromosome, position):
        if chromosome in self.interval_tree:
            if self.interval_tree[chromosome].overlaps(position):
                return True
        return False



def generate_snvs(vcf_file):
    """

    :param vcf_file:
    :return:
    """
    # vcf = namedtuple('vcf', ["chromosome", "position", "id", "reference", "alteration", "quality", "filter", "info"])

    with open(vcf_file) as vf_obj:

        for line in vf_obj:
            if line[0] != "#":
                sl = line.split()
                chromosome = sl[0]  # @TODO: Run chromosome checks
                position = sl[1]
                id = sl[2]  # For annotated SNPs
                reference = sl[3]
                alteration = sl[4]  # phred-scaled quality score for the assertion made in ALT
                quality = sl[5]
                filter = sl[6]
                info = "\t".join(sl[6:])
                # yield vcf_record(chromosome, position, id, reference, alteration, quality, filter, info)
                yield chromosome, position, id, reference, alteration, quality, filter, info


class VCFIntervalTree:

    def __init__(self):
        """

        """
        self.SNV_dict = {"+": dict(), "-": dict()}

    def add_snv(self, strand, chromosome, position, data):
        """

        :param chromosome:
        :param strand:
        :param position:
        :param reference:
        :param alteration:
        :return:
        """
        # reference, alteration
        try:
            self.SNV_dict[strand][chromosome][position:position+1] = data
        except KeyError:
            self.SNV_dict[strand][chromosome] = IntervalTree()
            self.SNV_dict[strand][chromosome][position:position+1] = data


    def get_snvs_within_range(self, chromosome, strand, start, stop):
        """

        :param chromosome:
        :param strand:
        :param start:
        :param stop:
        :return:
        """
        return self.SNV_dict[strand][chromosome][start:stop]



