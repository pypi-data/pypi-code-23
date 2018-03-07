import pandas as pd
from biomart import BiomartServer


class connect_biomart():
    def __init__(self, ref_version="GRCh37"):
        """
        Function to establish connection with BioMart server.

        Parameters
        ----------
        ref_version : Human database version

        Output
        ------
        None
        """

        # Connect to the server
        ## We need to remove the trailing /martview in the url
        # https://github.com/sebriois/biomart/issues/15

        try:
            print('#[LOG]: Establishing connection with Ensembl biomart')
            if ref_version in ['GRCh37']:
                server = BiomartServer('http://grch37.ensembl.org/biomart')
            elif ref_version in ['GRCh38']:
                server = BiomartServer('http://www.ensembl.org/biomart')
            else:
                print('#[ERR]: Version not valid, select between "GRCh37" or "GRCh38"')
                return()

            # Make the connection to the dataset of interest
            ensembl_connection = server.datasets['hsapiens_gene_ensembl']
        except:
            print('#[ERR]: The connection could not be stablished')
            return()

        print('#[LOG]: Connection established with database, version -> ' + ref_version)
        self.conn = ensembl_connection

        return None


    def query_biomart(self, filters, attributes):
        '''
        Function to query BioMart with the NMs.

        Parameters
        ----------
        nm_list: list
            List of NM ids. Query.

        Returns
        -------
        data : list
            List containing ENST_id, gene name and NM id.
        '''

        if not isinstance(filters, dict):
            raise Exception('Filters must be a dictionary')

        if not isinstance(attributes, list):
            raise Exception('Attributes must be a dictionary')

        # Do the query against ensembl
        response = self.conn.search({
            'filters': filters,
            'attributes': attributes
            })

        # response format is TSV
        data = []
        for line in response.iter_lines():
            line = line.decode('utf-8')
            data.append(line.split("\t")[0:len(data)])

        return(data)


    def query_relation_nm_enst(self, nm_list):
        '''
        Function to query BioMart with the NMs.

        Parameters
        ----------
        nm_list : list
            List of NM ids. Query.

        Output: Dataframe containing ENST_id, gene name and NM id.
        '''
        # Do the query against ensembl
        print('#[LOG]: Querying database...')

        response = self.conn.search({
            'filters': {
                'refseq_mrna': nm_list
            },
            'attributes': [
                'ensembl_transcript_id', 'refseq_mrna', 'external_gene_name',
            ]
            })

        # response format is TSV
        data = []
        for line in response.iter_lines():
            line = line.decode('utf-8')
            data.append(line.split("\t"))

        # insert the data into a dataframe
        nm_enst = pd.DataFrame(data)
        if nm_enst.empty:
            raise Exception("NM has no ensembl transcript -> " + nm_list)

        nm_enst.columns = ['ENST', 'RefSeq', 'gene']

        print('#[LOG]: Regions recovered: ' + str(len(nm_enst.index)))

        return nm_enst
