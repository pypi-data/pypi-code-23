# ---------------------------------------------------------------------------------------#
# ----------------------------------------------------------------------------- HEADER --#

"""
:author:
    Jared Webber
    

:synopsis:
    

:description:
    

:applications:
    
:see_also:
   
:license:
    see license.txt and EULA.txt 

"""

# ---------------------------------------------------------------------------------------#
# ---------------------------------------------------------------------------- IMPORTS --#
import os
import xml.etree.ElementTree as et
from ...utils.io import Autovivification, IO

# ---------------------------------------------------------------------------------------#
# -------------------------------------------------------------------------- FUNCTIONS --#

# ---------------------------------------------------------------------------------------#
# ---------------------------------------------------------------------------- CLASSES --#

class ReadObjectXML(object):
    '''
    This class reads an XML file and returns the data as a dictionary
    '''
    def __init__(self, xml_path):
        '''
        method takes and stores a path on disk
        :param xml_path:
        '''
        self.xml_path = xml_path
        self.obj_dict = None

    def validate(self):
        """
        validates the stored path
        """

        if not os.path.isfile(self.xml_path):
            IO.error("I could not find the xml located here '%s'" % self.xml_path)
            return None
        return True

    def read_xml(self):
        """
        Reads in the contents of the dictionary.
        """
        result = self.validate()
        if not result:
            return None
        xml_fh = et.parse(self.xml_path)
        root = xml_fh.getroot()
        xml_nodes = root.getchildren()
        xml_dict = Autovivification()
        for xml_node in xml_nodes:
            proj_nodes = xml_node.getchildren()
            for proj_node in proj_nodes:
                IO.debug("The Project Node: %s" % proj_node.tag)
                data_nodes = proj_node.getchildren()
                for data_node in data_nodes:
                    xml_dict[xml_node.tag][proj_node.tag][data_node.tag] = \
                                                    data_node.attrib['value']
        self.obj_dict = xml_dict
        return self.obj_dict