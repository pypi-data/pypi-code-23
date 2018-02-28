import dataplug
import dataplug.utils

################################################
class Graph():

    def __init__(self,
                 domain,
                 client_config={},
                 ):
        """ Graph operations

            :param domain: acting domain. for now graph operations can only
            happen on one domain. A multi-domain feature could be nice for
            problems that need the semantic for domain-based discrimination.
            domain source and destination should be encoded somewhere in
            documents or somewhere.

        """

        client = dataplug.Client(domain, client_config)

    def create_graph(self):
        """ Create an Arango graph with given arguments
        """
        pass

    def hierarchical_outbounds(self, from_collection, to_collection):
        pass

