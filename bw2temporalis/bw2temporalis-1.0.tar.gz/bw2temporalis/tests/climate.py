# -*- coding: utf-8 -*-
from __future__ import print_function, unicode_literals
from eight import *

#~from ..dynamic_ia_methods import DynamicIAMethod, dynamic_methods
#~from ..utils import get_function_name
# from bw2data import Database, Method, databases, methods
# from bw2calc import LCA


from bw2data import Database,config#,projects
from bw2data.tests import BW2DataTest as BaseTestCase
from ..dyn_methods.timedependent_lca import time_dependent_LCA
from ..dyn_methods.method_creation import create_climate_methods

from bw2io import bw2setup

import numpy as np
#~import warnings


db_bio = Database(config.biosphere)

class ClimateMetricsTestCase(BaseTestCase):
    def create_db(self):
        bw2setup()
        create_climate_methods()
        data = {
            ("clima", "co2"):{
                'name':"co2",
                'exchanges': [
                    {
                        'amount': 1,
                        'input': (db_bio.name, '349b29d1-3e58-4c66-98b9-9d1a076efd2e'), #fossil fuel carbon dioxide thus normal CF
                        'type': 'biosphere'
                    },
                ],
                'type': 'process',
            },
            ('clima', 'ch4'): {
                'name':"ch4",
                'exchanges': [
                    {
                        'amount': 1,
                        'input': (db_bio.name, 'da1157e2-7593-4dfd-80dd-a3449b37a4d8'), #Methane non fossil thus normal CF
                        'type': 'biosphere'
                    },
                ],
                'type': 'process',
            },

            ('clima', 'ch4_fossil'): {
                'name':"ch4_fossil",
                'exchanges': [
                    {
                        'amount': 1,
                        'input': (db_bio.name, '0795345f-c7ae-410c-ad25-1845784c75f5'), #Methane fossil thus consider conversion to co2
                        'type': 'biosphere'
                    },
                ],
                'type': 'process',
            },
            
            ('clima', 'co2bio_test'): {
                'name':"co2bio_test",
                'exchanges': [
                    {
                        'amount': 1,
                        'input': (db_bio.name, 'cc6a1abb-b123-4ca6-8f16-38209df609be'), #biogenic carbon dioxide 
                        'type': 'biosphere'
                    },
                ],
                'type': 'process',
            }

        }
        db = Database('clima')
        db.write(data)
        
    def test_dynamic_gwp(self):
        """test dynamic GWP"""
        self.create_db()
        
        print(time_dependent_LCA({("clima", "co2"):1},dynIAM='GWP'))
        print(time_dependent_LCA({("clima", "co2bio_test"):1},dynIAM='GWP'))
        print(time_dependent_LCA({("clima", "ch4"):1},dynIAM='GWP'))
        print(time_dependent_LCA({("clima", "ch4_fossil"):1},dynIAM='GWP'))      
        
        self.assertTrue(np.allclose(time_dependent_LCA({("clima", "co2"):1},dynIAM='GWP'),1)) #co2 fossil
        self.assertTrue(np.allclose(time_dependent_LCA({("clima", "co2bio_test"):1},dynIAM='GWP'),0.43,0.1)) #co2 biogenic
        self.assertTrue(np.allclose(time_dependent_LCA({("clima", "ch4"):1},dynIAM='GWP'),28,1)) #ch4 
        self.assertTrue(np.allclose(time_dependent_LCA({("clima", "ch4_fossil"):1},dynIAM='GWP'),29,1)) #ch4 fossil

        
