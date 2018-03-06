# -*- coding: utf-8 -*-
from __future__ import print_function, unicode_literals
from eight import *

from bw2data import Database,config,projects
# 
# ##To make get_forest_keys() work the method downstream_bio() below need to be added to bw2data.backends.peewee.proxies
    # def downstream_bio(self):
        # return Exchanges(
            # self.key,
            # ##kind="technosphere",
            # reverse=True
        # )
        # 
        
def get_static_forest_keys():
    """get the key of the forest sequestation processes in the set `forest`.
    Needed to consider forest sequestation dynamic in already installed dbs that 
    are static.
    When unit processes from other databases need to be evaluated dynamically is enough to add their name 
    to the set set `forest` inside the function.
    
    #Wrapped into a function otherwise it points to the default project if temporalis
    is imported before the current project is set """
    #they are all underbark, check if the bark CO2 is considered or not...if needed
    
    
    ei_22 = ["hardwood, Scandinavian, standing, under bark, in forest",
    "hardwood, standing, under bark, in forest",
    "eucalyptus ssp., standing, under bark, u=50%, in plantation",
    "meranti, standing, under bark, u=70%, in rainforest",
    "softwood, standing, under bark, in forest",
    "azobe (SFM), standing, under bark, in rain forest",
    "paraná pine, standing, under bark, in rain forest",
    "softwood, Scandinavian, standing, under bark, in forest"]

    ei_32_33 = [
    "softwood forestry, paraná pine, sustainable forest management",
     "hardwood forestry, mixed species, sustainable forest management",
     "hardwood forestry, beech, sustainable forest management",
     "softwood forestry, spruce, sustainable forest management",
     "hardwood forestry, meranti, sustainable forest management",
     "hardwood forestry, azobe, sustainable forest management",
     "softwood forestry, pine, sustainable forest management",
     #"import of roundwood, azobe from sustainable forest management, CM, debarked", # no
     #"import of roundwood, meranti from sustainable forest management, MY, debarked", # no
     "softwood forestry, mixed species, sustainable forest management",
     "hardwood forestry, oak, sustainable forest management",
     "hardwood forestry, birch, sustainable forest management",
     "hardwood forestry, eucalyptus ssp., sustainable forest management"
     ]
    
    #it should be the first one, but as it is not temporalis must be the second
    #~estelle=[
    #~'_Wood waste, sorted at panel plant, 20% water on dry mass basis/ EU U',
            #~'_Wood construction waste, 20% water on dry mass basis',
            #~]
    estelle=[
    #'_Allocation correction, spruce, 20% water on dry basis',
 #'_Aqueous microporous paint for wood, SIPEV/FR S_26082014',
 #'_Aqueous phase coating, SIPEV/FR S_20140527',
  #'_Polyurethane glue, Bostik, at plant/FR S_20140627',
 #'_Transport, lorry >28t, fleet average/CH S_litre',
 #'Polyethylene, HDPE, granulate, at plant/RER',

 '_Beech industrial roundwood, 80% water on dry mass basis, at forest road/FR S_20120830',
 '_Douglas-fir industrial roundwood, 65% water on dry mass basis, at forest road/FR S_20120830',
 '_Maritime pine industrial roundwood, 100% water on dry mass basis, at forest road/FR S_20120830',
 '_Oak industrial roundwood, 80% water on dry mass basis, at forest road/FR S_20120830',
 '_Scotch pine industrial roundwood, 104% water on dry mass basis, at forest road/FR S_20120830',
 '_Spruce industrial roundwood, 111% water on dry mass basis, at forest road/FR S_20120830',
 '_Wood waste, sorted at panel plant, 20% water on dry mass basis/ EU U',
 '_Wood construction waste, 20% water on dry mass basis',
 ]

            
            
    test=['co2bio_test']

    #dunno why this below returns skips some datasets
    #FORMIT_forest=[x['name'] for x in Database(db) if x['name'].split(',')[-1]==' NPP' for db in ['BAU0', 'BAU26', 'BAU45', 'BAU85', 'SCEN2_45', 'SCEN3_45', 'SCEN4_45', 'SCEN5_45', 'SCEN6_45']]

    #~FORMIT_forest=[]
    #~for db in ['BAU0', 'BAU26', 'BAU45', 'BAU85', 'SCEN2_45', 'SCEN3_45', 'SCEN4_45', 'SCEN5_45', 'SCEN6_45','trial']:
        #~FORMIT_forest.extend([x['name'] for x in Database(db) if x['name'].split(',')[-1]==' biogenic'])

    forest = set( ei_22 + ei_32_33 + estelle + test )# + FORMIT_forest)
    projects.set_current("{}".format(projects.current)) #need to do this otherwise uses default project if imported before setting the proj
    db = Database(config.biosphere)
    
    #search 'Carbon dioxide, in air' sequestered from processes in `forest` (empty set when biopshere not existing like in tests)
    return set() if not db else \
           set([x.output.key for x in db.get('cc6a1abb-b123-4ca6-8f16-38209df609be').upstream(kinds=None) if x.output.get('name') in forest])
