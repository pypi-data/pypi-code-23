from __future__ import print_function

from variantgrid_api.api import VariantGridAPI


def gene_list_handle_args(args):
    api = VariantGridAPI.from_args(args)

    if args.pk:
        genes = api.get_gene_list_genes(pk=args.pk)
    elif args.name:
        genes = api.get_gene_list_genes(category=args.category, name=args.name)
    
    for gene in genes:
        print(gene)