from __future__ import print_function

import json
from variantgrid_api.api import VariantGridAPI


def annotation_handle_args(args):
    api = VariantGridAPI.from_args(args)
    ret = None
    if args.gene_id:
        ret = api.gene_annotation(args.gene_id)
    elif args.gene:
        ret = api.gene_annotations(args.gene)
    elif args.variant:
        ret = api.variant_annotation(args.variant)

    print(json.dumps(ret, indent=4, sort_keys=True))
    