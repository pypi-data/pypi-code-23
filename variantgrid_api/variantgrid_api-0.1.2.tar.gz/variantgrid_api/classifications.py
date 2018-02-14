from __future__ import print_function

from collections import defaultdict
from datetime import datetime
import variantgrid_api
from variantgrid_api.api import VariantGridAPI

from variantgrid_api.variant_classification_vcf import VARIANTCLASSIFICATION_ID, \
    VARIANTCLASSIFICATION_ZYGOSITY, VARIANTCLASSIFICATION_GROUP, CLASSIFICATION, \
    VARIANT_GRID_INFO_DICT, INFO_SEPARATOR
from variantgrid_api.vcf_utils import get_vcf_header_lines, get_info


def write_variant(classifications_for_variant):
    # All loci should be the same
    variant = classifications_for_variant[0]["variant"]
    locus = variant["locus"]
    
    columns = [locus["chrom"],
               locus["position"],
               '.', # ID
               locus["ref"],
               variant["alt"],
               '.', # qual
               '.', ] # filter
    
    
    MERGE_COLUMNS = {"id" : VARIANTCLASSIFICATION_ID,
                     "zygosity" : VARIANTCLASSIFICATION_ZYGOSITY,
                     "classification_group" : VARIANTCLASSIFICATION_GROUP,
                     "classification_id" : CLASSIFICATION}
    merged_columns = defaultdict(list)
    for c in classifications_for_variant:
        for k, info_col in MERGE_COLUMNS.items():
            merged_columns[info_col].append(c.get(k))

    info_dict = {} # "VARIANT_GRID_ID" : variant["id"]}
    for (k, values_list) in merged_columns.items():
        if any(values_list):
            strings_list = map(str, [i or '' for i in values_list])
            info_dict[k] = INFO_SEPARATOR.join(strings_list)
    columns.append(get_info(info_dict))
    print(*columns, sep='\t')
    


def get_classifications(args):
    api = VariantGridAPI.from_args(args)

    classifications = [] 
    if args.all:
        classifications = api.variant_classifications_all(args.classification)
    elif args.gene:
        classifications = api.variant_classifications_for_gene(args.gene, args.classification)
    elif args.dbsnp:
        classifications = api.variant_classifications_for_dbsnp(args.dbsnp, args.classification)
    elif args.locus:
        classifications = api.variant_classifications_for_locus(args.locus, args.classification)
    elif args.variant:
        classifications = api.variant_classifications_for_variant(args.variant, args.classification)
    return classifications

def get_private_command_line(args):
    ''' private means don't show password '''

    SECRET_PARAMS = ["password", "command"]
    GLOBAL_PARAMS = ["host", "port", "login"]
    
    global_options_list = []
    for p in GLOBAL_PARAMS:
        v = getattr(args, p)
        if v:
            global_options_list.append("--%s=%s" % (p, v))

    params = set(vars(args)) - set(SECRET_PARAMS + GLOBAL_PARAMS)
    options_list = []
    for p in params:
        v = getattr(args, p)
        if v:
            options_list.append("--%s=%s" % (p, v))
        
    params = {"global_options" : ' '.join(global_options_list),
              "command" : args.command,
              "options" : ' '.join(options_list)}
    return "vg_api %(global_options)s %(command)s %(options)s" % params


def write_vcf(top_lines, classifications):
    info_dict = VARIANT_GRID_INFO_DICT.copy()
    
    header_lines = get_vcf_header_lines(top_lines=top_lines, info_dict=info_dict)
    print('\n'.join(header_lines))

    # Group by variant_id
    classifications_for_variant = []
    last_variant_id = None
    for classification in classifications:
        variant_id = classification["variant"]["id"]
        if last_variant_id and last_variant_id != variant_id: # Different
            write_variant(classifications_for_variant)
            classifications_for_variant = []

        classifications_for_variant.append(classification)
        last_variant_id = variant_id
        
    if classifications_for_variant: # leftovers
        write_variant(classifications_for_variant)
    
    


def classifications_handle_args(args):
    classifications = get_classifications(args)
    vg_api_str = "##generated_by=%s by vg_api v%s" % (datetime.now(), variantgrid_api.__version__)
    command_line = "##command_line=%s" % get_private_command_line(args)
    top_lines = [vg_api_str, command_line]

    write_vcf(top_lines, classifications)

    