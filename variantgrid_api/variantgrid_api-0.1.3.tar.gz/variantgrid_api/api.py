import json
import logging
import os
import requests


class VariantGridAPI(object):
    def __init__(self, login=None, password=None, host='https://variantgrid.com', port=None):
        if login and password:
            self.auth = (login, password)
        else:
            self.auth = None
        self.host = host
        self.port = port
    
    @staticmethod
    def from_args(args):
        return VariantGridAPI(args.login,
                              args.password,
                              host=args.host,
                              port=args.port)
        
    
    @property
    def url(self):
        u = "%s" % self.host
        if self.port:
            u += ":%d" % self.port
        return u
    
    def get(self, path):
        url_path = os.path.join(self.url, path) + ".json"
        r = requests.get(url_path, auth=self.auth)
        r.raise_for_status()
        try:
            return json.loads(r.text)
        except Exception as e:
            logging.error("Couldn't decode: %s" % r.text)
            logging.error(e)
        return None
    
    def loci_variants(self, variant_string):
        ''' returns a list of variant objects for this loci '''
        pass

    def gene_annotation(self, ensembl_gene__id, version=None):
        return self.get('annotation/api/gene_id/%(ensembl_gene__id)s' % {'ensembl_gene__id' : ensembl_gene__id})

    def gene_annotations(self, gene_symbol, version=None):
        ''' This may return multiple annotations for multiple genes '''
        return self.get('annotation/api/gene/%(gene_symbol)s' % {'gene_symbol' : gene_symbol})

    def variant_annotation(self, variant_string, version=None):
        ''' variant_string can be ID, rsId, HGVS '''
        return self.get('annotation/api/variant/%(variant_string)s' % {'variant_string' : variant_string})


    def get_gene_list_genes(self, pk=None, category=None, name=None, version=None):
        ''' Use either PK or both (category, name) '''
        too_many = pk and any([category, name])
        too_few = pk is None and not all([category, name])
        if too_many or too_few:
            msg = "You need to supply either 'pk' OR both ('category' AND 'name') arguments"
            raise ValueError(msg)

        if pk:
            gene_list = self.get('snpdb/gene_list/%s' % pk)
        else:
            gene_list = self.get('snpdb/named_gene_list/%s/%s' % (category, name))
        return gene_list["genelistgene_set"]


    def _get_classification_json(self, url, classification=None):
        ''' so we can modify to stream JSON '''
        
        if classification:
            url = os.path.join(url, "classification", str(classification))
        return self.get(url)
    
    def variant_classifications_all(self, classification=None):
        return self._get_classification_json('variantclassification/api/classifications/all', classification)
    
    def variant_classifications_for_gene(self, gene_symbol, classification=None):
        url = 'variantclassification/api/classifications/gene/%(gene_symbol)s' % {'gene_symbol' : gene_symbol}   
        return self._get_classification_json(url, classification)

    def variant_classifications_for_dbsnp(self, dbsnp, classification=None):
        url = 'variantclassification/api/classifications/dbsnp/%(dbsnp)s' % {'dbsnp' : dbsnp}   
        return self._get_classification_json(url, classification)

    def variant_classifications_for_locus(self, locus_string, classification=None):
        url = 'variantclassification/api/classifications/locus/%(locus_string)s' % {'locus_string' : locus_string}   
        return self._get_classification_json(url, classification)

    def variant_classifications_for_variant(self, variant_string, classification=None):
        url = 'variantclassification/classifications/api/variant/%(variant_string)s' % {'variant_string' : variant_string}   
        return self._get_classification_json(url, classification)


    def _add_classification_json(self, path, classification, public):
        url_path = os.path.join(self.url, path) + ".json"
        data = {"classification" : classification,
                "public" : public}
        
        r = requests.post(url_path, auth=self.auth, json=data)
        r.raise_for_status()
        return r.text

    def add_classifications_for_dbsnp(self, dbsnp, classification, public=False):
        params = {'dbsnp' : dbsnp}
        url = 'variantclassification/api/add_classification/dbsnp/%(dbsnp)s' % params   
        return self._add_classification_json(url, classification, public)

    def add_classifications_for_variant(self, variant_string, classification, public=False):
        params = {'variant_string' : variant_string,}
        url = 'variantclassification/api/add_classification/variant/%(variant_string)s' % params   
        return self._add_classification_json(url, classification, public)



    def create_variant_classification(self, variant_string, classification):
        # Check whether the variant string is correct - get back 
        # Send up classification
        # Get back ID and return it
        pass