from __future__ import print_function

from variantgrid_api.api import VariantGridAPI


def add_classification_handle_args(args):
    api = VariantGridAPI.from_args(args)

    classification = None
    if args.dbsnp:
        classification = api.add_classifications_for_dbsnp(args.dbsnp, args.classification, args.public)
    elif args.variant:
        classification = api.add_classifications_for_variant(args.variant, args.classification, args.public)

    if classification:
        pk = classification["id"]
        gvc_url = "%s/variantclassification/view_genomic_variant_classification/%d" % (api.url, pk) 
        print("Created classification: %s" % gvc_url)
