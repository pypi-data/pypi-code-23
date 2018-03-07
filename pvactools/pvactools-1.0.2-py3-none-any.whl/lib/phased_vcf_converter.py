import vcf

class PhasedVcfConverter:
    def __init__(self, **kwargs):
        self.input_file  = kwargs['input_file']

    def parse(self):
        phased_entries = defaultdict(list)
        with open(self.input_file, 'r') as fh:
            reader = vcf.Reader(fh)
            sample = reader.samples[0]
            for entry in reader:
                if 'HP' not in entry.FORMAT.split(':'):
                    continue
                else:
                    phased_entries[entry.genotype(sample)['HP']].append(entry)
        phased_entries_for_variant = defaultdict(list)
        for key, entries in phased_entries.items():
            if len(entries) == 1:
                continue
            for entry in entries:
                for base in entry.genotype(sample).gt_bases:
                    if base == entry.REF:
                        continue
                    for other_entry in entries:
                        if entry == other_entry:
                            continue
                        phased_entries_for_variant[(entry.CHR, entry.POS, entry.REF, base)].append(other_entry)



