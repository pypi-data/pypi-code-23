#!/usr/bin/env python
# -*- coding: utf-8 -*-
''' A simple module to store sites from fusion tables '''
import ee

import ee.data
if not ee.data._initialized: ee.Initialize()

import csv
import requests
import functions
from geetools import tools


class Site(object):
    """ Site Class to store sites related to fusion tables """
    def __init__(self, name=None, id_ft=None, id_fld=None, name_fld=None,
                 n_feat=0):
        """
        :param name: name of the site
        :type name: str
        :param id_ft: Fusion Table ID
        :type id_ft: str
        :param id_fld: Name of the Fusion Table Field that contains the id for
            each individual site
        :type id_fld: str
        :param name_fld: Name of the Fusion Table Field that contains the name
            for each individual site
        :type name_fld: str
        :param n_feat: Number of features that contain the Fusion Table
        :type n_feat: int
        """
        self.name = name
        self.id_ft = id_ft
        self.id_fld = id_fld
        self.name_fld = name_fld
        self.n_feat = n_feat

    @property
    def ft(self):
        if self.id_ft:
            return ee.FeatureCollection("ft:"+self.id_ft)
        else:
            return None

    def filter_id(self, id):
        """ Filters the fusion table by the given id

        :param id: id to filter
        :type id: int
        :return: (ee.Geometry, region as a list of lists)
        :rtype: tuple
        """
        try:
            place = self.ft.filterMetadata(self.id_fld, "equals", id)
            place = ee.Feature(place.first())
            place = place.set("origin", self.name, "id", id)

            try:
                region = place.geometry().bounds().getInfo()['coordinates'][0]
            except AttributeError as ae:
                print ae
                region = place.getInfo()['coordinates'][0]
            except Exception as e:
                print e
                return None, None

            return place, region
        except Exception as e:
            # print "Hubo un error al filtrar el ID"
            print e
            return None, None


def from_csv(file, name="name", id_ft="id_ft", id_fld="id_fld",
             name_fld=None):
    """ Generates a dictionary of Sites from a csv file.

    :param name:
    :param id_ft:
    :param id_fld:
    :param name_fld:
    """
    sites = []
    with open(file) as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            params = [row[name], row[id_ft], row[id_fld]]
            params = params.append(row[name_fld]) if name_fld else params
            site = (row[name], Site(*params))
            sites.append(site)

    return dict(sites)


def from_gsheet(url, sheet, name=None, id_ft=None, id_fld=None, name_fld=None):
    """ Generates a dictionary of Sites from a Google SpreadSheet. It must be
    Public and shared to anyone. Doesn't use any API

    :param url:
    :param sheet:
    :param name: name of field that holds the name of the site
    :param id_ft: name of field that holds the id of the fusion table
    :param id_fld: name of field that holds the ID of the site
    :param name_fld:
    """
    content = requests.get(url)
    json = tools.execli(content.json, 10, 5)()
    sheet = json[sheet]
    sites = []

    for n, row in enumerate(sheet):
        if n == 0: continue
        if row[name] == "": continue
        # params = [row[name], row[id_ft], row[id_fld]]
        # print params
        # params = params.append(row[name_fld]) if name_fld else params
        site = (row[name], Site(name=row[name], id_ft=row[id_ft],
                                id_fld=row[id_fld], name_fld=row[name_fld]))
        sites.append(site)

    return dict(sites)

if __name__ == "__main__":
    '''
    list = from_gsheet("https://script.google.com/macros/s/AKfycbygukdW3tt8sCPcFDlkM" \
                       "nMuNu9bH5fpt7bKV50p2bM/exec?id=11hMJ-rI_VtRxcUl3GSpUtLQ1L3yfIj" \
                       "eApRAaZczHK28&sheet=Hoja1", "Hoja1", "NOMBRE", "ID_FT", "ID")

    for site in list:
        print site.name, site.id_ft
    '''
    import os
    path =  os.path.dirname(__file__)
    p = path.split("/")[:-1]
    path = "/"+os.path.join(os.path.join(*p), "data", "sites.csv")

    list2 = from_csv(path)

    for site in list2:
        s = list2[site]
        print site, list2[site].id_ft
        #print s.ft
        feat, region = s.filter_id(5000)
        print feat, region

        feat, region = s.filter_id(1)
        print region

