#!/usr/bin/env python2.7

import os
import urllib
import jinja2
import webapp2
import base64

import load_parameters as LP #This initializes all of the data
import query_data as QD
import json
import load_funcs as LF
import upload_datasets as UD
import password as PW
#import web_module_to_load as WMTL
#import upload_cloud_storage_to_datastore as UCSTD

class MainPage(webapp2.RequestHandler):
    @PW.passwordStatus("off", "guest", "guest")
    def get(self):
        #Load main meta data
        template_values =LP.siteJsonData
        template_values.update(  { "siteJsonVal": json.dumps(LP.siteJsonData)})
        defaultSearchTerm = LP.siteJsonData["defaultterm"]
        template_values["clickedButtonKey"] = template_values["defaultpanel"]
        template_values = fill_in_template_values(template_values, defaultSearchTerm)
        template_values["searchTerm"] = defaultSearchTerm
        template = LP.JINJA_ENVIRONMENT.get_template('index.html')
        
        self.response.write(template.render(template_values))

class Search(webapp2.RequestHandler):
    def post(self):
        template_values = LP.siteJsonData
        template_values.update(  { "siteJsonVal": json.dumps(LP.siteJsonData)})
        queryIn = self.request.get('searchTerm')
        template_values["clickedButtonKey"] = self.request.get('clickedButton')
        template_values["searchTerm"] = queryIn
        template_values = fill_in_template_values(template_values, queryIn)
        template = LP.JINJA_ENVIRONMENT.get_template('index.html')
        self.response.write(template.render(template_values))

def fill_in_template_values(template_values, searchTerm):
    #Load data for search term
    dataJson = QD.extract_data_for_term(searchTerm, LP.datasetModelDict, LP.searchlookupDict)
    
    data_template_values = {
            "dataJsonVal": json.dumps(dataJson)
    }
    template_values.update(data_template_values)

    #Load figure info
    figureJson = LF.json_load_byteified(open("static/figures.json"))
    figure_template_values = {
        "figureJsonVal": json.dumps(figureJson)
    }
    template_values.update(figure_template_values)

    #Load dataset info
    datasetJson = LF.json_load_byteified(open("static/datasets.json"))
    dataset_template_values = {
        "datasetJsonVal": json.dumps(datasetJson)
    }
    template_values.update(dataset_template_values)

    #Load sidebar
    sidebarJson = LF.json_load_byteified(open("static/sidebar.json"))
    buttonKeyNames = [[x[2], x[1]] for x in sidebarJson if x[0]=="BUTTON"]
    sidebar_template_values = {
            "sidebarJsonVal": json.dumps(sidebarJson),
            "buttonKeyNames": buttonKeyNames
    }
    template_values.update(sidebar_template_values)

    #Load panels
    panelJson = LF.json_load_byteified(open("static/panels.json"))
    panel_template_values = {
            "panelJsonVal": json.dumps(panelJson),
    }
    template_values.update(panel_template_values)
    
    #Load density csv files
    densityDict = dict()
    for i in figureJson:
        if figureJson[i]["figuretype"]=="density":
            data = LF.read_csv("static/" + figureJson[i]["densityfile"])
            densityDict[i] = dict()
            densityDict[i]["percentile"] = data[0]
            densityDict[i]["density"]  = data[1:]
    density_template_values = {
        "densityDictVal": json.dumps(densityDict),
    }
    template_values.update(density_template_values)

    #Load meta data terms // This will load for all datasets, the appropriate meta data. 
    searchMetaList = list()
    for i in figureJson:
        for j in figureJson[i]["paramList"]:
            if "meta" in j[3]:
                searchTerm = j[3].split("meta.")[1]
                metakey = figureJson[i]["metakey"]
                if (searchTerm, metakey) not in searchMetaList:
                    searchMetaList.append([searchTerm, metakey])
    metaDataDict = dict()
    for i in searchMetaList:
        searchTerm, metakey = i[0],i[1]
        data = QD.extract_data_for_term_and_dataset(searchTerm, LP.datasetModelDict, metakey)
        metaDataDict[metakey + "." + searchTerm] = data

    meta_data_template_values = {
        "metaDataDictVal": json.dumps(metaDataDict)
    }
    template_values.update(meta_data_template_values) 
    return template_values


class AuthTest(webapp2.RequestHandler):
  @PW.passwordStatus("on", "guest", "guest")
  def get(self):
     self.response.write("Toodles")

app = webapp2.WSGIApplication([
    ## Run on the production only ##
    ('/', MainPage), 
    ('/search', Search), 
#    ('/upload', UCSTD.Upload),
#    ('/transfer_to_storage', UCSTD.TransferToStorage), #For testing
#    ('/get_serving', UCSTD.Get_Serving_Urls_For_Sample), #For testing

    ## Run on local only #
    ('/loadLocal', UD.LocalUploadDatastore),
], debug=True)


