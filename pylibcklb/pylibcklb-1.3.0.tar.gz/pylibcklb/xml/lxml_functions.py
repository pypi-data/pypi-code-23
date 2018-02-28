## Lxml functions libary file for all functions related to lxml
#
# @file		    lxml_functions.py
# @author	    Tobias Ecklebe tobias.ecklebe@outlook.de
# @date		    05.11.2017
# @version	    0.2.0
# @note		    This file includes functions as libary that i think are great for different projects.\n\n
#               To use this file:  from pylibcklb.xml-library.lxml_functions import SomeClassOrFunction\n           
#
# @pre          The library was developed with python 3.6 64 bit  and lxml
#
# @bug          No bugs at the moment.
#
# @warning      No warnings at the moment
#
# @copyright    pylibcklb package
#               Copyright (C) 2017  Tobias Ecklebe
#
#               This program is free software: you can redistribute it and/or modify
#               it under the terms of the GNU Lesser General Public License as published by
#               the Free Software Foundation, either version 3 of the License, or
#               (at your option) any later version.
#
#               This program is distributed in the hope that it will be useful,
#               but WITHOUT ANY WARRANTY; without even the implied warranty of
#               MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#               GNU Lesser General Public License for more details.
#
#               You should have received a copy of the GNU Lesser General Public License
#               along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
import os  
import lxml                                                                    
from lxml import etree
from pylibcklb.ClassLibrary import cDebug 
from pylibcklb.FunctionLibrary import remove_prefix, remove_postfix, IsThereAKnownPrefix
from pylibcklb.metadata import PackageVariables
Debug = cDebug(PackageVariables.DebugLevel)

## Documentation of a method that updates a key value pair
# @param xmlitem The xml item that should be updated
# @param key The key that should be updated
# @param value The new value that be updated in the key
def UpdateKeyValuePair(xmlitem, key, value):
    Debug.PrintFunctionName(Debug.LEVEL_FUNCTIONENTRY)
    KeyList = xmlitem.keys()
    message = ''
    if key in KeyList:
        ValueInKey = xmlitem.get(key)
        if value != ValueInKey:
            xmlitem.set(key,value)
            return True, message
        else:
            message = 'The NewValue is not new'
            Debug.Print(Debug.LEVEL_All, message)
            return False, message
    #If the key is not in the list, we check if there is a key in the list,
    #that has an prefix
    elif any(key in s for s in KeyList):
        MatchingStringList = [s for s in KeyList if key in s]
        prefix = remove_postfix(MatchingStringList[0],key)
        Debug.Print(Debug.LEVEL_All, str('There is a key with prefix: (' + prefix + key + ') in the item.keys(): ' + str(KeyList)))
        Debug.Print(Debug.LEVEL_All, 'We remove the element with prefix from the xml tree, create an new element in the tree and then update the value')               
        ValueInKey = xmlitem.get(MatchingStringList[0])
        if value != ValueInKey:
            ChangeKeyName(xmlitem, MatchingStringList[0], key)
            xmlitem.set(key,value)
            return True, message
        else:
            message = 'The NewValue is not new'
            Debug.Print(Debug.LEVEL_All, message)
            return False, message
    else:
        message = 'There is no key: (' + key + ') in the item.keys(): ' + str(KeyList)
        Debug.Print(Debug.LEVEL_All, message)
        return False, message        

## Documentation of a method that changes the key name of an item in the
## tree over a delete the old key value pair and create a new one
# @param xmlitem The xml item where to change the key name
# @param key The key that should be changed
# @param NewKey The new name of the key
def ChangeKeyName(xmlitem, key, NewKey):
    Debug.PrintFunctionName(Debug.LEVEL_FUNCTIONENTRY)
    if key in xmlitem.keys():
        value = xmlitem.get(key)
        xmlitem.attrib.pop(key)
        xmlitem.set(NewKey,value)
    return

## Documentation for a method to remove all prefixes from the xml attributes.
# Only the enum prefix will be not removed, to get the drop down
#  @param xmlitem XML element to delte the prefixes from the attributes
#  @param ListOfPrefixes List of all used prefixes
def RemovePrefixFromXMLItemAttribute(xmlitem, ListOfPrefixes):
    for key in xmlitem.keys():
        ret = IsThereAKnownPrefix(key, ListOfPrefixes)
        if ret is not None:
            ValueInKey = xmlitem.get(key)   
            ret2 = IsThereAKnownPrefix(ValueInKey, ListOfPrefixes) 
            if ret2 is not None:
                if ret2 is not "ENUM_":
                    ValueInKey = remove_prefix(ValueInKey, ret2)
            xmlitem.attrib.pop(key)
            key = remove_prefix(key, ret)
            xmlitem.set(key,ValueInKey)

## Documentation for a method to convert etree.element into string
#  @param element XML element that should converted into an string
def XMLElementToString(element):
    root = etree.Element('OpenSCENARIO')
    root.append(element)
    return etree.tostring(root, pretty_print=True)

## Documentation for a method to convert an string into an xml element tree
#  @param XMLString The string to convert 
def ReadStringToXMLElementTree(XMLString):
    return etree.ElementTree(etree.XML(XMLString))

## Documentation for a method to read a xml file
#  The returned value is the parsed xml file
#  @param PathOfXMLFile The path of the xml file
def ReadXmlFile(PathOfXMLFile):

    filename, file_extension = os.path.splitext(PathOfXMLFile)
    if (file_extension == '.xosc' or file_extension == '.xsd' or file_extension == '.EFOSConfiguration'):
        parser = etree.XMLParser(remove_blank_text=True, remove_comments=True)
        try:
            with open(PathOfXMLFile) as XmlFile:                                                
                doc = etree.parse(XmlFile, parser)  
            XmlFile.close()
        except (OSError, IOError) as e:
            return e, None  
        return True, doc  
    else:
        e = 'Wrong file format! \nfile format reguired is: \nxosc/xsd/EFOSConfiguration\nfile format deliverd is: ' + file_extension
        return e, None 

## Documentation for a method to validate a xml schema file
#  The returned value is true if the file is valid and false if not
#  @param PathOfXMLSchemaFile The path of the xml schema or specification file
def ValidateXmlSchemaFile(PathOfXMLSchemaFile):

    State, doc = ReadXmlFile(PathOfXMLSchemaFile)

    if State == True:         

        Debug.Print(cDebug.LEVEL_All, "Validating schema ...")
        try:                                                                        
            schema = etree.XMLSchema(doc)                                           
        except lxml.etree.XMLSchemaParseError as e:
            Debug.Print(cDebug.LEVEL_All, "Schema fails with:")
            Debug.Print(cDebug.LEVEL_All, e)
            return e, None          
        Debug.Print(cDebug.LEVEL_All, "Schema OK")
        return True, schema     
    else:
        return State, None                                                                       

## Documentation for a method to validate a xml file against a xml schema file
#  The returned value is true if the file is valid and false if not
#  @param PathOfXMLSchemaFile The path of the xml schema or specification file
#  @param PathOfXMLFile The path of the xml file to validate
def ValidateXmlFile(PathOfXMLSchemaFile, PathOfXMLFile):

    State, schema = ValidateXmlSchemaFile(PathOfXMLSchemaFile)

    if State == True:         
    
        State2, doc = ReadXmlFile(PathOfXMLFile)

        if State2 == True:      
                                                            
            Debug.Print(cDebug.LEVEL_All, "Validating document ...")                                      
            try:                                                                        
                schema.assertValid(doc)                                                 
            except lxml.etree.DocumentInvalid as e: 
                Debug.Print(cDebug.LEVEL_All, "Document fails with:")                                    
                Debug.Print(cDebug.LEVEL_All, e)  
                return e                                                              
                                                                                
            Debug.Print(cDebug.LEVEL_All, "Document OK")
            return True
        else:
            return State2 
    else:
        return State

## Documentation for a method to validate a xml tree against a xml schema file
#  The returned value is true if the file is valid and false if not
#  @param PathOfXMLSchemaFile The path of the xml schema or specification file
#  @param XMLTree The xml tree to validate
def ValidateXmlTree(PathOfXMLSchemaFile, XMLTree):

    State, schema = ValidateXmlSchemaFile(PathOfXMLSchemaFile)

    if State == True:
                                                                                                                                                   
        Debug.Print(cDebug.LEVEL_All, "Validating document ...")                                        
        try:                                                                        
            schema.assertValid(XMLTree)                                                 
        except lxml.etree.DocumentInvalid as e: 
            Debug.Print(cDebug.LEVEL_All, "Document fails with:")
            Debug.Print(cDebug.LEVEL_All, e)
            return e                                                              
                                                                                
        Debug.Print(cDebug.LEVEL_All, "Document OK")
        return True
    
    else:
        return State

## Documentation of a method save xml tree to file
# @param XMLTree Xml tree element that should be validate and write to file
# @param PathOfXMLFile The path of the xml file to write
def SaveXMLTree(XMLTree,PathOfXMLFile):
    try:
        XMLTree.write(PathOfXMLFile, xml_declaration=True, encoding='utf-8', pretty_print=True) 
    except (OSError, IOError) as e:
        return e   

    return True

## Documentation of a method to validate and save xml tree to file
# @param XMLTree Xml tree element that should be validate and write to file
# @param PathOfXMLSchemaFile The path of the xml schema or specification file
# @param PathOfXMLFile The path of the xml file to write
def ValidateAndSaveXMLTree(XMLTree, PathOfXMLSchemaFile, PathOfXMLFile):

    ret = ValidateXmlTree(PathOfXMLSchemaFile ,XMLTree)

    if  ret != True:
        return ret  
  
    return SaveXMLTree(XMLTree,PathOfXMLFile)

## Documentation of a method to iterate over an xml file and return an generator
# @note Sourcecode comes from: https://stackoverflow.com/questions/9856163/using-lxml-and-iterparse-to-parse-a-big-1gb-xml-file
# @code
#from lxml import etree
#
#xmlfile = '/path/to/xml/file.xml'
#element_list = []
#ret = iterate_xml(xmlfile)
#for element in ret:
#    print(element.tag)
#    if element.tag == 'element':
#        element_list.append(element)
# @endcode
# @param xmlfile Path to the xml file
def iterate_xml(xmlfile):
    doc = etree.iterparse(xmlfile, events=('start', 'end'))
    _, root = next(doc)
    start_tag = None
    for event, element in doc:
        if event == 'start' and start_tag is None:
            start_tag = element.tag
        if event == 'end' and element.tag == start_tag:
            yield element
            start_tag = None
            root.clear()

## Documentation of a method to find expression in xml tree without defining the namespace 
# @note Sourcecode comes from: https://stackoverflow.com/questions/5572247/how-to-find-xml-elements-via-xpath-in-python-in-a-namespace-agnostic-way
# @code
#doc = '''<root xmlns="http://really-long-namespace.uri"
#    xmlns:other="http://with-ambivalent.end/#">
#    <other:elem/>
#</root>'''
#tree = lxml.etree.fromstring(doc)
#print xpath_ns(tree, '/root')
#print xpath_ns(tree, '/root/elem')
#print xpath_ns(tree, '/root/other:elem')
# @endcode
# @param tree Tree to search in
# @param expr Expression to search
def xpath_ns(tree, expr):
    "Parse a simple expression and prepend namespace wildcards where unspecified."
    qual = lambda n: n if not n or ':' in n else '*[local-name() = "%s"]' % n
    expr = '/'.join(qual(n) for n in expr.split('/'))
    nsmap = dict((k, v) for k, v in tree.nsmap.items() if k)
    return tree.xpath(expr, namespaces=nsmap)

## Documentation of a method to check if type is one of the xml built-in data
## types
# Reference: https://www.w3schools.com/xml/schema_simple_attributes.asp
#xs:string
#xs:decimal
#xs:integer
#xs:boolean
#xs:date
#xs:time
# @param Type The type to check
# @return True if the type is a basetype, false if not
def IsBuiltInDataType(Type):
    Types = ['xsd:double', 'xsd:string', 'xsd:dateTime', 'xsd:unsignedShort', 'xsd:boolean', 'xsd:unsignedInt', 'xsd:int']

    if Type in Types:
        return True
    else:
        return False

## Documentation of a method to check if type is an enumeration type or not
# @param Type The type to check
# @return True if the type is a enumeration, false if not
def IsEnumType(Type):
    if Type.startswith("Enum_"):
        return True
    else:
        return False

## Documentation of a method to get a prefilled element for a defined base type
# @param Type The type to get a value for
# @return Return an string with the correct element in it or error message if
# type is not an base type
def GetValueForBaseType(Type):

    if Type == 'xsd:double':
        return "DOUBLE_0,000"
    elif Type == 'xsd:string':
        return "Muster"
    elif Type == 'xsd:dateTime':
        return "2017-01-01T00:00:00.00000"
    elif Type == 'xsd:unsignedShort':
        return "INT_0"
    elif Type == 'xsd:boolean':
        return "ENUM_false,true"
    elif Type == 'xsd:unsignedInt':
        return "INT_0"
    elif Type == 'xsd:int':
        return "INT_0"

## Documentation of a method to check the type and return a prefilled element
## when type is base type
# @param Type The type to get a value for
# @param RetValue Value to return that holds an string with the correct element
# in it or an error message if type is not an base type
# @return Return True or False if type is not an base type
def IsBaseTypeGetValue(Type, RetValue):
    ret = IsBuiltInDataType(Type)
    if ret == True:
        RetValue[0] = GetValueForBaseType(Type)
    else:
        RetValue[0] = str('The type: "' + str(Type) + '" is no element of xml base types')

    Debug.Print(cDebug.LEVEL_All, str('Result of check in method "IsBaseTypeGetValue": ' + RetValue[0]))
    return ret

def SearchInTreeForElementType(TypeDefRoot, ElementType):    

    #search in type def root for element type and get if definded the type
    expr = "//*[@name='" + str(ElementType) + "']"
    nsmap = dict((k, v) for k, v in TypeDefRoot.nsmap.items() if k)
    xsd_item_list = TypeDefRoot.xpath(expr, name = ElementType, namespaces=nsmap)

    if xsd_item_list != []:
        #We say that there is only one element of this type in the xml type
        #defs
        return xsd_item_list[0]
    else:
        return None

def SearchInXMLForTag(XML, Tag):    
    Debug.PrintFunctionName(Debug.LEVEL_FUNCTIONENTRY)
    Debug.Print(Debug.LEVEL_FUNCTIONENTRY, ('Element tag to find is: ' + Tag))
    return  XML.getroot().find('.//'+Tag)

## Documentation of a method to check the type and return a prefilled element
## when type is enumeration type
# @param Type The type to get a value for
# @param RetValue Value to return that holds an string with the correct element
# in it or an error message if type is not an base type
# @param TypeDefRoot Root of the type def xml
# @return Return True or False if type is not an base type
def IfEnumTypeGetValue(Type, RetValue, TypeDefRoot):
    RetValue.clear()
    ret = IsEnumType(Type)
    if ret == True:
        xsd_item = SearchInTreeForElementType(TypeDefRoot, Type)

        element_list = xpath_ns(xsd_item, 'restriction/enumeration')    
        RetValueList = []
        for element in element_list:
            RetValueList.append(element.get('value'))
        #RetValue.append(RetValueList[0])
        RetValue.append('ENUM_'+",".join(str(x) for x in RetValueList))
    else:
        RetValue.append(str('The type: "' + str(Type) + '" is no element of xml enumeration types'))

    Debug.Print(cDebug.LEVEL_All, str('Result of check in method "IfEnumTypeGetValue": ' + RetValue[0]))
    return ret

def IsParentAChoiceElement(TypeDefRoot, item):
    ChoiceExpression = '{' + TypeDefRoot.nsmap.get('xsd') + '}'+'choice'
    if item.getparent().tag == ChoiceExpression:
        return True
    else:
        return False
