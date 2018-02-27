#!/usr/bin/env python2.7


def create_json_to_load(self):
    '''
    setKey:
    buttonName:
    setNameLong:
    citation:
    citationLink:
    info
    searchType
    '''
    import json


    dict_list = list()

    #First, put in the main dict:(idx is 0)
    meta_dict = dict()
    meta_dict['nameOfSite'] = self.sitename
    meta_dict['appId'] = self.appid
    meta_dict['labName'] = self.labname
    if self.lablink[0:4]!="http": self.lablink = "http://" + self.lablink
    meta_dict['labLink'] = self.lablink
    meta_dict['defaultTerm'] = self.default

    dict_list.append(meta_dict)

    #Next, load in the dataset data (idx is 1:)
    for dataset in self.datasets:
        dataset_dict = dict()
        dataset_dict['setKey'] = dataset.setkey
        dataset_dict['buttonName'] = dataset.btnname
        dataset_dict['setNameLong'] = dataset.setname
        dataset_dict['citation'] = dataset.citetext
        dataset_dict['citationLink'] = dataset.citelink
        dataset_dict['info'] = dataset.info
        dataset_dict['searchType'] = dataset.search
        dict_list.append(dataset_dict)

    fileOUT = open("web/web_data/dataset.data.json", "w")
    json.dump(dict_list, fileOUT)
    fileOUT.close()

