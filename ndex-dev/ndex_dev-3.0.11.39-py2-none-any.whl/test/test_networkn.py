__author__ = 'aarongary'

import unittest
import ndex
import ndex.client as nc
from ndex.networkn import  FilterSub, NdexGraph
import json
import uuid
#import time
import pickle
import sys
import os
import cPickle
path_this = os.path.dirname(os.path.abspath(__file__))

class NetworkNTests(unittest.TestCase):
    #==============================
    # TEST LARGE NETWORK
    #==============================
    @unittest.skip("Temporary skipping")
    def test_data_to_type(self):
        self.assertTrue(self, ndex.networkn.data_to_type('true','boolean'))
        print(type(ndex.networkn.data_to_type('1.3','double')))
        print(type(ndex.networkn.data_to_type('1.3','float')))
        print(type(ndex.networkn.data_to_type('1','integer')))
        print(type(ndex.networkn.data_to_type('1','long')))
        print(type(ndex.networkn.data_to_type('1','short')))
        print(type(ndex.networkn.data_to_type('1','string')))
        list_of_boolean = type(ndex.networkn.data_to_type('["true","false"]','list_of_boolean'))
        print(list_of_boolean)

        list_of_double = ndex.networkn.data_to_type('[1.3,1.4]','list_of_double')
        print(list_of_double)

        list_of_float = ndex.networkn.data_to_type('[1.3,1.4]','list_of_float')
        print(list_of_float)

        list_of_integer = ndex.networkn.data_to_type('[1,4]','list_of_integer')
        print(list_of_integer)

        list_of_long = ndex.networkn.data_to_type('[1,4]','list_of_long')
        print(list_of_long)

        list_of_short = ndex.networkn.data_to_type('[1,4]','list_of_short')
        print(list_of_short)

        list_of_string = ndex.networkn.data_to_type(['abc'],'list_of_string')
        print(list_of_string)

    #@unittest.skip("Temporary skipping")
    def test_edge_float_type(self):
        G = NdexGraph()
        n_a = G.add_new_node(name='AAAA')
        n_b = G.add_new_node(name='BBBB')
        n_c = G.add_new_node(name='CCCC')
        n_d = G.add_new_node(name='DDDD')

        e_1 = G.add_edge(n_a, n_b, 10, {'weight': 1.234})
        e_2 = G.add_edge(n_a, n_c, 11, {'weight': 2.554})
        e_3 = G.add_edge(n_a, n_d, 12, {'weight': 5.789})
        e_4 = G.add_edge(n_b, n_c, 13, {'weight': 2.011})
        e_5 = G.add_edge(n_b, n_d, 14, {'weight': 7.788})

        print(json.dumps(G.to_cx()))
        G.upload_to('http://dev.ndexbio.org', 'scratch', 'scratch')


    @unittest.skip("Temporary skipping")
    def test_pos(self):
        path_to_network = os.path.join(path_this, 'tmp.pkl')
        with open(path_to_network, 'rb') as f:
            tmp2 = cPickle.load(f)
            tmp2.subnetwork_id = 1
            count = 0
            for n, v in tmp2.pos.items():
                if count % 200 == 0:
                    print(n)
                if count > 2700:
                    print(n)
                count += 1
            tmp2.upload_to('http://dev.ndexbio.org', 'scratch', 'scratch')
            print 'test'


    @unittest.skip("Temporary skipping")
    def test_visibility_param(self):
        G = NdexGraph()
        n_a = G.add_new_node(name='AAAA')
        n_b = G.add_new_node(name='BBBB')
        n_c = G.add_new_node(name='CCCC')
        n_d = G.add_new_node(name='DDDD')

        e_1 = G.add_edge(n_a, n_b, 10, {'weight': 1.234, 'testProp1': 'ABC'})
        e_2 = G.add_edge(n_a, n_c, 11, {'weight': 2.554, 'testProp1': 'DEF'})
        e_3 = G.add_edge(n_a, n_d, 12, {'weight': 5.789, 'testProp1': 'GHI'})
        e_4 = G.add_edge(n_b, n_c, 13, {'weight': 2.011, 'testProp1': 'RST'})
        e_5 = G.add_edge(n_b, n_d, 14, {'weight': 7.788, 'testProp1': 'XYZ'})
        indexed_fields = ['testProp1']

        print(json.dumps(G.to_cx()))
        network_uri = G.upload_to('http://dev.ndexbio.org', 'scratch', 'scratch', indexed_fields=indexed_fields, visibility='PUBLIC')

        print network_uri

        #network_id = uuid.UUID('{' + network_uri[-36:] + '}')
        network_id = network_uri[-36:]

    @unittest.skip("Temporary skipping")
    def test_visibility_param(self):
        G = NdexGraph(server="http://public.ndexbio.org", uuid='09f3c90a-121a-11e6-a039-06603eb7f303') # "21106ea7-cbba-11e7-ad58-0ac135e8bacf")
        serialized = pickle.dumps(G.to_cx(), protocol=0)
        print('Serialized memory:', sys.getsizeof(serialized))
        #niceCx = ndex2.create_nice_cx_from_server(server='public.ndexbio.org', uuid='21106ea7-cbba-11e7-ad58-0ac135e8bacf')



        #test_nc = nc.Ndex(host='http://dev.ndexbio.org', username='scratch', password='scratch', debug=True)
        #search_results = test_nc.search_network_nodes('ec7a1324-ca35-11e7-ab01-06832d634f41', search_string='DDDD', limit=5)

        #print(search_results)

if __name__ == '__main__':
    unittest.main()
