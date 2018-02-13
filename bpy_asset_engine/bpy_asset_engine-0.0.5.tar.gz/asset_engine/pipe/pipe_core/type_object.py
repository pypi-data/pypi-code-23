#!/usr/bin/env python
#SETMODE 777

#----------------------------------------------------------------------------------------#
#------------------------------------------------------------------------------ HEADER --#

"""
:author:
    Jared Webber
    jmw150530

:synopsis:
    The module holds the classes for a Project and Asset and their functions

:description:
    The classes in this file read an XML document and generate objects based upon
    the data found therein

"""

#----------------------------------------------------------------------------------------#
#----------------------------------------------------------------------------- IMPORTS --#

# Built-in
import os
from xml.dom import minidom
# Third party

# Internal

# External
from .pipe_utils import ReadObjectXML
from . import pipe_object as PO
from ...utils.io import Autovivification, IO
#----------------------------------------------------------------------------------------#
#--------------------------------------------------------------------------- FUNCTIONS --#

#----------------------------------------------------------------------------------------#
#----------------------------------------------------------------------------- CLASSES --#

class Project(object):
    """
    This class defines a Project object.
    The class finds an XML document on disc, then generates the required objects/values -
    for the project
    """
    def __init__(self):
        """
        Store path to Projects.XML
        """
        self.xml_path         = None
        self.project_dict     = None
        self.project_data     = []

    def get_project_objects(self):
        """
        Gets the values of the project XML that was read from read_xml method
        """
        self.find_xml()
        self.project_dict = self.read_xml()
        all_keys = self.project_dict['project'].keys()
        # IO.debug("The Keys: %s" % all_keys)
        for key in all_keys:
            temp_dict = self.project_dict['project'][key]
            project_data = PO.ProjectObject(**temp_dict)
            self.project_data.append(project_data)
        return self.project_data

    def find_xml(self):
        """
        Finds the XML document and returns it as a variable
        """
        self.xml_path = os.path.dirname(__file__) + '/projects.xml'
        return self.xml_path

    def read_xml(self):
        """
        Reads the data in the XML File using ReadObjectXML class
        """

        read_xml_data = ReadObjectXML(self.xml_path)
        read_xml_data.read_xml()
        project_dict = read_xml_data.obj_dict
        return project_dict

    @staticmethod
    def read_disk(path):
        if os.path.isdir(path):
            return [PO.ProjectObject(name=name, path=os.path.abspath(os.path.join(path, name)))
                    for name in os.listdir(path) if "desktop.ini" not in name and "." not in name]
        else:
            return []
        # else:
        #     os.makedirs(path, exist_ok=True)
        #     return [AssetObject(name=name, path=os.path.abspath(os.path.join(path, name)))
        #             for name in os.listdir(path) if "desktop.ini" not in name]


class AssetType(object):
    def __init__(self):
        self.xml_path = None
        self.type_dict = None
        self.type_data = []

    @staticmethod
    def read_disk(path):
        if os.path.isdir(path):
            return [PO.AssetTypeObject(name=name, path=os.path.abspath(os.path.join(path, name)))
                    for name in os.listdir(path) if "desktop.ini" not in name]
        else:
            return []


class Asset(object):
    """
    This class defines an Asset object.
    The class finds an XML document on disc, then generates the required objects/values -
    for the asset.
    This class's methods and functions behave exactly the same as the Project class
    """

    def __init__(self):
        self.xml_path       = None
        self.asset_dict     = None
        self.asset_data     = []


    def find_xml(self):
        self.xml_path = os.path.dirname(__file__) + '/assets.xml'
        return self.xml_path

    def read_xml(self):
        read_xml_data = ReadObjectXML(self.xml_path)
        read_xml_data.read_xml()
        asset_dict = read_xml_data.obj_dict
        return asset_dict


    def get_asset_objects(self):
        self.find_xml()
        self.asset_dict = self.read_xml()
        all_keys = self.asset_dict.keys()
        for key in all_keys:
            temp_dict = self.asset_dict[key]
            asset_data = PO.AssetObject(**temp_dict)
            self.asset_data.append(asset_data)
        return self.asset_data

    def read_disk(self, path):
        if os.path.isdir(path):
            return [PO.AssetObject(name=name, path=os.path.abspath(os.path.join(path, name)))
                    for name in os.listdir(path) if "desktop.ini" not in name]
        # else:
        #     os.makedirs(path, exist_ok=True)
        #     return [AssetObject(name=name, path=os.path.abspath(os.path.join(path, name)))
        #             for name in os.listdir(path) if "desktop.ini" not in name]
    @staticmethod
    def find_assets(path):
        if os.path.isdir(path):
            return [PO.AssetObject(name=name, path=os.path.abspath(os.path.join(path, name)))
                    for name in os.listdir(path) if os.path.isfile((os.path.join(path, name)))
                    and os.path.join(path, name).rsplit('.')[1] == 'blend']
        else:
            return []


