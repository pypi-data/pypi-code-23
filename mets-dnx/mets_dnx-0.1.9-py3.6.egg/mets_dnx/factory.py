import hashlib
import json
import os
import re
import time

from lxml import etree as ET

from pydc import factory as dc_factory
from pymets import mets_factory as mf
from pymets import mets_model as mm
from pydnx import factory as dnx_factory

def generate_md5(filepath, block_size=2**20):
    """For producing md5 checksums for a file at a specified filepath."""
    m = hashlib.md5()
    with open(filepath, "rb") as f:
        while True:
            buf = f.read(block_size)
            if not buf:
                break
            m.update(buf)
    return m.hexdigest()


def build_amdsec(amdsec, tech_sec=None, rights_sec=None, 
                 source_sec=None, digiprov_sec=None):
    amd_id = amdsec.attrib['ID']
    amd_tech = ET.SubElement(
                    amdsec, 
                    "{http://www.loc.gov/METS/}techMD", 
                    ID=amd_id + "-tech")
    amd_rights = ET.SubElement(
                    amdsec,
                    "{http://www.loc.gov/METS/}rightsMD",
                    ID=amd_id + "-rights")
    amd_source = ET.SubElement(
                    amdsec,
                    "{http://www.loc.gov/METS/}sourceMD",
                    ID=amd_id + "-source")
    amd_digiprov = ET.SubElement(
                    amdsec,
                    "{http://www.loc.gov/METS/}digiprovMD",
                    ID=amd_id + "-digiprov")

    for el in [amd_tech, amd_rights, amd_source, amd_digiprov]:
        mdWrap = ET.SubElement(
                        el, 
                        "{http://www.loc.gov/METS/}mdWrap",
                        MDTYPE="OTHER", OTHERMDTYPE="dnx")
        xmlData = ET.SubElement(mdWrap, "{http://www.loc.gov/METS/}xmlData")
        if (el.tag == "{http://www.loc.gov/METS/}techMD" and 
                tech_sec != None):
            xmlData.append(tech_sec)
        elif (el.tag == "{http://www.loc.gov/METS/}techMD" and 
                tech_sec == None):
            xmlData.append(ET.Element("dnx",
                xmlns="http://www.exlibrisgroup.com/dps/dnx"))

        if (el.tag == "{http://www.loc.gov/METS/}rightsMD" and 
                rights_sec != None):
            xmlData.append(rights_sec)
        elif (el.tag == "{http://www.loc.gov/METS/}rightsMD" and 
                rights_sec == None):
            xmlData.append(ET.Element("dnx",
                xmlns="http://www.exlibrisgroup.com/dps/dnx"))

        if (el.tag == "{http://www.loc.gov/METS/}sourceMD" and 
                source_sec != None):
            xmlData.append(source_sec)
        elif (el.tag == "{http://www.loc.gov/METS/}sourceMD" and 
                source_sec == None):
            xmlData.append(ET.Element("dnx",
                xmlns="http://www.exlibrisgroup.com/dps/dnx"))

        if (el.tag == "{http://www.loc.gov/METS/}digiprovMD" and 
                digiprov_sec != None):
            xmlData.append(digiprov_sec)
        elif (el.tag == "{http://www.loc.gov/METS/}digiprovMD" and 
                digiprov_sec == None):
            xmlData.append(ET.Element("dnx",
                xmlns="http://www.exlibrisgroup.com/dps/dnx"))


def _build_ie_dmd_amd(mets,
                   ie_dmd_dict=None,
                   generalIECharacteristics=None,
                   cms=None,
                   webHarvesting=None,
                   objectIdentifier=None,
                   accessRightsPolicy=None,
                   eventList=None):
    # first off, build ie-dmdsec
    # check if ie_dmd_dict is a single dictionary inside a list
    # (which is the convention for the METS factory, but not necessary for
    # the DC Factory)
    if type(ie_dmd_dict) == list and len(ie_dmd_dict) == 1:
        ie_dmd_dict = ie_dmd_dict[0]
    dc_record = dc_factory.build_dc_record(ie_dmd_dict)
    dmdsec = ET.SubElement(
                mets,
                "{http://www.loc.gov/METS/}dmdSec",
                ID="ie-dmd")
    mdwrap = ET.SubElement(
                dmdsec,
                "{http://www.loc.gov/METS/}mdWrap",
                MDTYPE="DC")
    xmldata = ET.SubElement(
                mdwrap,
                "{http://www.loc.gov/METS/}xmlData")
    xmldata.append(dc_record)

    # build ie amd section
    ie_amdsec = ET.SubElement(
                    mets,
                    "{http://www.loc.gov/METS/}amdSec",
                    ID="ie-amd")
    if ((generalIECharacteristics != None) 
            or (cms != None) 
            or (objectIdentifier != None)
            or (webHarvesting != None)):
        ie_amd_tech = dnx_factory.build_ie_amdTech(
            generalIECharacteristics=generalIECharacteristics,
            objectIdentifier=objectIdentifier,
            CMS=cms,
            webHarvesting=webHarvesting)
    else:
        ie_amd_tech = None
    if (accessRightsPolicy != None):
        ie_amd_rights = dnx_factory.build_ie_amdRights(
            accessRightsPolicy=accessRightsPolicy)
    else:
        ie_amd_rights = None
    if (eventList != None):
        ie_amd_digiprov = dnx_factory.build_ie_amdDigiprov(event=eventList)
    else:
        ie_amd_digiprov = None
    # TODO (2016-10-03): add functionality for ie_amdSourceMD
    ie_amd_source = None
    build_amdsec(
            ie_amdsec,
            ie_amd_tech,
            ie_amd_rights,
            ie_amd_digiprov,
            ie_amd_source)

def build_mets(ie_dmd_dict=None,
                pres_master_dir=None, 
                modified_master_dir=None,
                access_derivative_dir=None,
                cms=None,
                webHarvesting=None,
                generalIECharacteristics=None,
                objectIdentifier=None,
                accessRightsPolicy=None,
                eventList=None,
                input_dir=None,
                digital_original=False):

    mets = mf.build_mets()

    _build_ie_dmd_amd(mets,
            ie_dmd_dict=ie_dmd_dict,
            generalIECharacteristics=generalIECharacteristics,
            cms=cms,
            webHarvesting=webHarvesting,
            objectIdentifier=objectIdentifier,
            accessRightsPolicy=accessRightsPolicy,
            eventList=eventList)

    mf.build_amdsec_filegrp_structmap(
        mets,
        ie_id="ie1", 
        pres_master_dir=pres_master_dir,
        modified_master_dir=modified_master_dir,
        access_derivative_dir=access_derivative_dir,
        digital_original=digital_original,
        input_dir=input_dir)


    # Create representation_level and file_level amdsecs, based on
    # the filegrp details
    file_groups = mets.findall('.//{http://www.loc.gov/METS/}fileGrp')
    for file_group in file_groups:
        rep_id = file_group.attrib['ID']
        rep_type = mets.find('.//{%s}structMap[@ID="%s-1"]/{%s}div' % 
            ('http://www.loc.gov/METS/', rep_id, 'http://www.loc.gov/METS/')
            ).attrib['LABEL']
        
        if rep_type == 'Preservation Master':
            pres_type = 'PRESERVATION_MASTER'
            pres_location = pres_master_dir
        elif rep_type == 'Modified Master':
            pres_type = 'MODIFIED_MASTER'
            pres_location = modified_master_dir
        elif rep_type == 'Derivative Copy':
            pres_location = access_derivative_dir
            pres_type = 'DERIVATIVE_COPY'
        else:
            pres_type = None
            pres_location = '.'

        rep_amdsec = mets.xpath("//mets:amdSec[@ID='%s']" % 
                str(rep_id + '-amd'), namespaces=mets.nsmap)[0]
        general_rep_characteristics = [{'RevisionNumber': '1', 
                'DigitalOriginal': str(digital_original).lower(),
                'usageType': 'VIEW',
                'preservationType': pres_type}]
        rep_amd_tech = dnx_factory.build_rep_amdTech(
            generalRepCharacteristics=general_rep_characteristics)
        rep_amd_rights = None
        rep_amd_digiprov = None
        rep_amd_source = None
        build_amdsec(
            rep_amdsec,
            tech_sec=rep_amd_tech, 
            rights_sec=rep_amd_rights,
            source_sec=rep_amd_source, 
            digiprov_sec=rep_amd_digiprov)

        # create amdsec for files
        for fl in file_group.findall('./{http://www.loc.gov/METS/}file'):
            fl_id = fl.attrib['ID']
            fl_amdsec = None
            fl_amdsec = mets.xpath("//mets:amdSec[@ID='%s']" % 
                    str(fl_id + '-amd'), namespaces=mets.nsmap)[0]
            file_original_location = os.path.join(input_dir,
                fl.find('./{http://www.loc.gov/METS/}FLocat').attrib[
                        '{http://www.w3.org/1999/xlink}href'])
            file_original_name = os.path.normpath(file_original_location).split(os.path.sep)[-1]
            file_label = os.path.splitext(file_original_name)[0]
            file_size_bytes = os.path.getsize(file_original_location)
            last_modified = time.strftime(
                    "%Y-%m-%dT%H:%M:%S",
                    time.localtime(os.path.getmtime(file_original_location)))
            created_time = time.strftime(
                    "%Y-%m-%dT%H:%M:%S",
                    time.localtime(os.path.getctime(file_original_location)))
            general_file_characteristics = [{
                'fileOriginalPath': file_original_location,
                'fileSizeBytes': str(file_size_bytes),
                'fileModificationDate': last_modified,
                'fileCreationDate': created_time,
                'fileOriginalName': file_original_name,
                'label': file_label}]

            file_fixity =  [{
                'fixityType': 'MD5',
                'fixityValue': generate_md5(file_original_location)}]

            fl_amd_tech = dnx_factory.build_file_amdTech(
                generalFileCharacteristics=general_file_characteristics,
                fileFixity=file_fixity)
            build_amdsec(fl_amdsec, tech_sec=fl_amd_tech)


    # clean up identifiers so they are consistent with Rosetta requirements
    for element in mets.xpath(".//*[@ID]"):
        element.attrib['ID'] = re.sub('ie[0-9]+\-', '', element.attrib['ID'])
        element.attrib['ID'] = re.sub(
                'rep([0-9]+)\-file([0-9]+)',
                r'fid\2-\1',
                element.attrib['ID'])
    for element in mets.xpath(".//*[@ADMID]"):
        element.attrib['ADMID'] = re.sub(
                'ie[0-9]+\-rep([0-9]+)\-file([0-9]+)-amd',
                r'fid\2-\1-amd',
                element.attrib['ADMID'])
        element.attrib['ADMID'] = re.sub(
                'ie[0-9]+\-rep([0-9]+)-amd',
                r'rep\1-amd',
                element.attrib['ADMID'])
    for element in mets.xpath(".//*[@FILEID]"):
        element.attrib['FILEID'] = re.sub(
                'ie[0-9]+\-rep([0-9])+\-file([0-9]+)',
                r'fid\2-\1',
                element.attrib['FILEID'])

    # 2017-02-16 (SM): Modify the file label in the structmaps so that it does
    # not contain file extensions. This is an NDHA requirement, so I am 
    # reluctant to put this on the actual METS factory level.
    # 2017-02-16 (SM): Add an order count to the divs in the structmap.
    struct_maps = mets.findall('./{http://www.loc.gov/METS/}structMap')
    for struct_map in struct_maps:
        top_div_count = 0
        top_divs = struct_map.findall('./{http://www.loc.gov/METS/}div')
        for top_div in top_divs:
            # top_div_count += 1
            # top_div.attrib['ORDER'] = str(top_div_count)
             # Insert "Table of Contents" div between the file divs and the top div
            toc_element = ET.Element('{http://www.loc.gov/METS/}div')
            toc_element.attrib['LABEL'] = 'Table of Contents'
            top_div.append(toc_element)
            lower_div_count = 0
            file_divs = top_div.findall('./{http://www.loc.gov/METS/}div[@TYPE="FILE"]')
            for file_div in file_divs:
                lower_div_count += 1
                # 2017-07-20: Removing "ORDER" attribute
                # file_div.attrib['ORDER'] = str(lower_div_count)
                file_div.attrib["LABEL"] = os.path.splitext(file_div.attrib["LABEL"])[0]
                # 2017-07-19: commented out line below, not sure why it was there in the first place!
                # del file_div.attrib['TYPE']
                toc_element.append(file_div)
    return mets


def build_single_file_mets(ie_dmd_dict=None,
                filepath=None,
                cms=None,
                webHarvesting=None,
                generalIECharacteristics=None,
                objectIdentifier=None,
                accessRightsPolicy=None,
                eventList=None,
                digital_original=False):
    mets = mf.build_mets()
    _build_ie_dmd_amd(mets,
            ie_dmd_dict=ie_dmd_dict,
            generalIECharacteristics=generalIECharacteristics,
            cms=cms,
            webHarvesting=webHarvesting,
            objectIdentifier=objectIdentifier,
            accessRightsPolicy=accessRightsPolicy,
            eventList=eventList)

    # Build rep amdsec
    rep_amdsec = ET.Element("{http://www.loc.gov/METS/}amdSec", ID="rep1-amd")
    general_rep_characteristics = [{'RevisionNumber': '1', 
            'DigitalOriginal': str(digital_original).lower(),
            'usageType': 'VIEW',
            'preservationType': 'PRESERVATION_MASTER'}]
    rep_amd_tech = dnx_factory.build_rep_amdTech(
        generalRepCharacteristics=general_rep_characteristics)
    rep_amd_rights = None
    rep_amd_digiprov = None
    rep_amd_source = None
    build_amdsec(
        rep_amdsec,
        tech_sec=rep_amd_tech, 
        rights_sec=rep_amd_rights,
        source_sec=rep_amd_source, 
        digiprov_sec=rep_amd_digiprov)
    mets.append(rep_amdsec)

    # Build file amdsec
    fl_amdsec = ET.Element("{http://www.loc.gov/METS/}amdSec", ID="fid1-1-amd")
    file_original_location = filepath
    file_original_name = os.path.normpath(file_original_location).split(os.path.sep)[-1]
    file_label = os.path.splitext(file_original_name)[0]
    file_size_bytes = os.path.getsize(file_original_location)
    last_modified = time.strftime(
            "%Y-%m-%dT%H:%M:%S",
            time.localtime(os.path.getmtime(file_original_location)))
    created_time = time.strftime(
            "%Y-%m-%dT%H:%M:%S",
            time.localtime(os.path.getctime(file_original_location)))
    general_file_characteristics = [{
        'fileOriginalPath': file_original_location,
        'fileSizeBytes': str(file_size_bytes),
        'fileModificationDate': last_modified,
        'fileCreationDate': created_time,
        'fileOriginalName': file_original_name,
        'label': file_label}]

    file_fixity =  [{
        'fixityType': 'MD5',
        'fixityValue': generate_md5(file_original_location)}]

    fl_amd_tech = dnx_factory.build_file_amdTech(
        generalFileCharacteristics=general_file_characteristics,
        fileFixity=file_fixity)
    build_amdsec(fl_amdsec, tech_sec=fl_amd_tech)
    mets.append(fl_amdsec)

    # build filesec
    filename = os.path.basename(filepath)
    file_label = os.path.splitext(filename)[0]
    filesec = mm.FileSec()
    filegrp = mm.FileGrp(ID="rep1", ADMID="rep1-amd", USE="VIEW")
    filesec.append(filegrp)

    file_el = mm.File(ID='fid1-1', ADMID="fid1-1-amd")
    filegrp.append(file_el)

    flocat = mm.FLocat(LOCTYPE="URL", href=filename)
    file_el.append(flocat)

    mets.append(filesec)
    
    # build structmap
    structmap = mm.StructMap(ID="rep1-1", TYPE="PHYSICAL")

    div_1 = mm.Div(LABEL="Preservation Master")
    structmap.append(div_1)

    div_2 = mm.Div(LABEL="Table of Contents")
    div_1.append(div_2)

    div_3 = mm.Div(LABEL=file_label, TYPE="FILE")
    div_2.append(div_3)

    fptr = mm.Fptr(FILEID='fid1-1')
    div_3.append(fptr)

    mets.append(structmap)

    return mets


def _build_fl_amd_from_json(mets, file_no, rep_no, item):
    fl_amd_sec = mm.AmdSec(ID="fid{}-{}-amd".format(file_no, rep_no))
    fileOriginalName = None
    fileSizeBytes = None
    md5sum = None
    fileCreationDate = None
    fileModificationDate = None
    note = None
    # events = None

    gfc = {} # general file characteristics
    fixity = {}
    events = {}
    gfc['fileOriginalPath'] = item['fileOriginalPath']
    for key in item.keys():
        if key == 'fileOriginalName':
            gfc['fileOriginalName'] = item[key]
        if key == 'fileSizeBytes':
            gfc['fileSizeBytes'] = item[key]
        if key == 'fileCreationDate':
            gfc['fileCreationDate'] = item[key]
        if key == 'fileModificationDate':
            gfc['fileModificationDate'] = item[key]
        if key == 'note':
            gfc['note'] = item[key]
        if key == 'label':
            gfc['label'] = os.path.splitext(item[key])[0]

        # fixity values
        if key.upper() == 'MD5':
            fixity['fixityType'] = 'MD5'
            fixity['fixityValue'] = item[key]
        # provenance values
        if key == 'events':
            events = item[key]

    # Check the supplied fixity to make sure it can be reproduced
    # TODO: Come back to this!
    # fileSizeBytes = None
    # if md5sum and fileOriginalpath:
    #     fileSizeBytes = os.path.getsize(fileOriginalpath)
    #     checksum = generate_md5(fileOriginalpath)
    #     if md5sum != checksum:
    #         raise ValueError("could not reproduce MD5 sum for {}: Expected {}, got {}".format(
    #             fileOriginalPath, md5sum, checksum))

    # reset any empty dicts to None value
    if len(gfc) == 0:
        gfc = None
    if len(fixity) == 0:
        fixity = None
    if len(events) == 0:
        events = None

    fl_amd_tech = dnx_factory.build_file_amdTech(
        generalFileCharacteristics=[gfc],
        fileFixity=[fixity])
    fl_amd_digiprov = dnx_factory.build_ie_amdDigiprov(
        event=events)
    # yes, the call to ie amdDigiprov is intentional,
    # as we don't yet have a file digiprov builder. Should be fine though.

    build_amdsec(fl_amd_sec, tech_sec=fl_amd_tech, digiprov_sec=fl_amd_digiprov)
    mets.append(fl_amd_sec)


def _parse_json_for_fl_amd(mets, rep_no, json_doc):
    if type(json_doc) == str:
        rep_dict = json.loads(json_doc)
    else:
        rep_dict = json_doc
    file_no = 1
    for item in rep_dict:
        _build_fl_amd_from_json(mets, file_no, rep_no, item)
        file_no += 1


def _parse_json_for_filegrp(filegrp, rep_no, json_doc, input_dir):
    if type(json_doc) == str:
        rep_dict = json.loads(json_doc)
    else:
        rep_dict = json_doc
    file_no = 1
    for item in rep_dict:
        try:
            file_el = mm.File(ID="fid{}-{}".format(file_no, rep_no),
                              ADMID="fid{}-{}-amd".format(file_no, rep_no))
            flocat = mm.FLocat(LOCTYPE="URL", href=item['fileOriginalPath'])
            file_el.append(flocat)
            filegrp.append(file_el)
            file_no += 1
        except KeyError:
            print("The following json was missing an important value: {}".format(item))


def _recursively_build_divs(div, pathlist, rep_no, file_no, json_doc):
    if type(json_doc) == str:
        rep_dict = json.loads(json_doc)
    else:
        rep_dict = json_doc
    newdiv = div.find('./{http://www.loc.gov/METS/}div[@LABEL="%s"]' % (pathlist[0]))
    if newdiv != None:
        _recursively_build_divs(newdiv, pathlist[1:], rep_no, file_no, json_doc)
    else:
        if len(pathlist) == 1:
            if 'label' in rep_dict.keys():
                label = os.path.splitext(rep_dict['label'])[0]
            else:
                label = rep_dict['fileOriginalName']
            newdiv = mm.Div(LABEL="{}".format(label),
                            TYPE="FILE")
            fptr = mm.Fptr(FILEID="fid{}-{}".format(file_no, rep_no))
            newdiv.append(fptr)
            div.append(newdiv)
        else:
            newdiv = mm.Div(LABEL="{}".format(pathlist[0]))
            div.append(newdiv)
            _recursively_build_divs(newdiv, pathlist[1:], rep_no, file_no, rep_dict)


def _parse_json_for_structmap(div, rep_no, json_doc):
    if type(json_doc) == str:
        rep_dict = json.loads(json_doc)
    else:
        rep_dict = json_doc
    file_no = 0
    for item in rep_dict:
        file_no += 1
        pathlist = os.path.normpath(item['fileOriginalPath']).split(os.path.sep)
        # This above may rely on the OS running the script to be the
        # same type that made the path. Not sure on this, but it sounds like
        # a good unit test case...
        _recursively_build_divs(div, pathlist, rep_no, file_no, item)



def _build_rep_amdsec(mets, rep_no, digital_original, preservation_type):
    rep_amdsec = ET.Element("{http://www.loc.gov/METS/}amdSec", ID="rep{}-amd".format(rep_no))
    general_rep_characteristics = [{'RevisionNumber': '1', 
            'DigitalOriginal': str(digital_original).lower(),
            'usageType': 'VIEW',
            'preservationType': preservation_type}]
    rep_amd_tech = dnx_factory.build_rep_amdTech(
        generalRepCharacteristics=general_rep_characteristics)
    rep_amd_rights = None
    rep_amd_digiprov = None
    rep_amd_source = None
    build_amdsec(
        rep_amdsec,
        tech_sec=rep_amd_tech, 
        rights_sec=rep_amd_rights,
        source_sec=rep_amd_source, 
        digiprov_sec=rep_amd_digiprov)
    mets.append(rep_amdsec)

def build_mets_from_json(ie_dmd_dict=None,
                pres_master_json=None, 
                modified_master_json=None,
                access_derivative_json=None,
                cms=None,
                webHarvesting=None,
                generalIECharacteristics=None,
                objectIdentifier=None,
                accessRightsPolicy=None,
                eventList=None,
                input_dir=None,
                digital_original=False):
    """Build a METS XML file using JSON-formatted data describing the 
    rep structures, rather than directory paths."""
    mets = mf.build_mets()
    _build_ie_dmd_amd(mets,
        ie_dmd_dict=ie_dmd_dict,
        generalIECharacteristics=generalIECharacteristics,
        cms=cms,
        webHarvesting=webHarvesting,
        objectIdentifier=objectIdentifier,
        accessRightsPolicy=accessRightsPolicy,
        eventList=eventList)

    # start building fileSec here, but do not append it until after all
    # the amdSecs have been added.
    filesec = mm.FileSec()

    # start building list of structmaps here, but do not append it until after
    # the fileSec has been added.
    structmap_list = []


    rep_no = 1
    if pres_master_json != None:
        pmd = json.loads(pres_master_json)
        pm_rep_no = rep_no

        # Build rep AMD Sec
        _build_rep_amdsec(mets, rep_no, digital_original, 'PRESERVATION_MASTER')
        # run through json structure and find files, assembling their
        # filepaths along the way
        _parse_json_for_fl_amd(mets, rep_no, pres_master_json)
        # construct fileSec details for rep
        filegrp = mm.FileGrp(ID="rep{}".format(rep_no),
                    ADMID="rep{}-amd".format(rep_no))
        _parse_json_for_filegrp(filegrp, rep_no, pres_master_json, input_dir)
        filesec.append(filegrp)
        # Build the structmap for this rep
        structmap = mm.StructMap(ID="rep{}-1".format(rep_no), TYPE="PHYSICAL")
        div1 = mm.Div(LABEL='Preservation Master')
        structmap.append(div1)
        div2 = mm.Div(LABEL='Table of Contents')
        div1.append(div2)
        mets.append(structmap)
        _parse_json_for_structmap(div2, rep_no, pres_master_json)
        structmap_list.append(structmap)
        rep_no += 1
    if modified_master_json != None:
        mm_rep_no = rep_no
        mmd = json.loads(modified_master_json)
        _build_rep_amdsec(mets, rep_no, digital_original, 'MODIFIED_MASTER')
        _parse_json_for_fl_amd(mets, rep_no, modified_master_json)
        # construct fileSec details for rep
        filegrp = mm.FileGrp(ID="rep{}".format(rep_no),
                    ADMID="rep{}-amd".format(rep_no))
        _parse_json_for_filegrp(filegrp, rep_no, modified_master_json, input_dir)
        filesec.append(filegrp)
        # Build the structmap for this rep
        structmap = mm.StructMap(ID="rep{}-1".format(rep_no), TYPE="PHYSICAL")
        div1 = mm.Div(LABEL='Modified Master')
        structmap.append(div1)
        div2 = mm.Div(LABEL='Table of Contents')
        div1.append(div2)
        mets.append(structmap)
        _parse_json_for_structmap(div2, rep_no, modified_master_json)
        structmap_list.append(structmap)
        rep_no += 1
    if access_derivative_json != None:
        add = json.loads(access_derivative_json)
        ad_rep_no = rep_no
        _build_rep_amdsec(mets, rep_no, digital_original, 'DERIVATIVE_COPY')
        _parse_json_for_fl_amd(mets, rep_no, access_derivative_json)
        # construct fileSec details for rep
        filegrp = mm.FileGrp(ID="rep{}".format(rep_no),
                    ADMID="rep{}-amd".format(rep_no))
        _parse_json_for_filegrp(filegrp, rep_no, access_derivative_json, input_dir)
        filesec.append(filegrp)
        # Build the structmap for this rep
        structmap = mm.StructMap(ID="rep{}-1".format(rep_no), TYPE="PHYSICAL")
        div1 = mm.Div(LABEL='Access Derivative')
        structmap.append(div1)
        div2 = mm.Div(LABEL='Table of Contents')
        div1.append(div2)
        mets.append(structmap)
        _parse_json_for_structmap(div2, ad_rep_no, access_derivative_json)
        structmap_list.append(structmap)
        rep_no += 1

    mets.append(filesec)

    for structmap in structmap_list:
        mets.append(structmap)

    return mets
