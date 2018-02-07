"""
A converter class, able to verify, extract and submit
important tumor diagnostic information from a ZIP archive
to CentraXX.
"""
import os
import sys
import uuid
from zipfile import ZipFile
from mtbparser.snv_utils import *
from .mtbfiletype import MtbFileType
from .mtbconverter_exceptions import MtbUnknownFileType
from .mtbconverter_exceptions import MtbIncompleteArchive
from .mtbconverter_exceptions import MtbUnknownBarcode
from .datasetinstance import DataSetInstance
from .patientdataset import PatientDataSet
from .cx_profiles import *
from mtbparser.snv_parser import SnvParser
from mtbparser.snv_utils import SSnvHeader
from datetime import datetime

TEMP_BASE_PATH = "/tmp"

FILETYPE_HEADER = {
    MtbFileType.GERM_SNV: GSnvHeader,
    MtbFileType.SOM_SNV: SSnvHeader,
    MtbFileType.GERM_CNV: CnvHeader,
    MtbFileType.SOM_CNV: CnvHeader,
    MtbFileType.SOM_SV: SsvHeader,
    MtbFileType.META: MetaData
    }

VERSIONS = {
    MtbFileType.GERM_SNV: 'QBIC_GERMLINE_SNV_V{}'.format(GERMLINE_SNV_VERSION) ,
    MtbFileType.SOM_SNV: 'QBIC_SOMATIC_SNV_V{}'.format(SOMATIC_SNV_VERSION),
    MtbFileType.GERM_CNV: 'QBIC_GERMLINE_CNV_V{}'.format(GERMLINE_CNV_VERSION),
    MtbFileType.SOM_CNV: 'QBIC_SOMATIC_CNV_V{}'.format(SOMATIC_CNV_VERSION),
    MtbFileType.SOM_SV: 'QBIC_SOMATIC_SV_V{}'.format(SOMATIC_SV_VERSION),
    MtbFileType.META: 'QBIC_METADATA_V{}'.format(METADATA_VERSION)
}

class MtbConverter():

    def __init__(self, zip_file, sample_code, patient_code):
        pyxb.utils.domutils.BindingDOMSupport.DeclareNamespace(cx.Namespace, 'cxx')
        self._root = cx.CentraXXDataExchange()
        self._zip_file = zip_file
        self._sample_code = sample_code
        self._patient_code = patient_code
        self._filelist = {}
        self._snvlists = {}
        self._tmp_dir = TEMP_BASE_PATH + os.path.sep + "tmp_uktdiagnostics_" + uuid.uuid4().hex
        os.mkdir(self._tmp_dir)
        self._verify()
        self._extract()
        self._cleanup()

    def _extract(self):
        try:
            self._zip_file.extractall(path=self._tmp_dir)
        except Exception as exc:
            print(exc)
            self._cleanup()
            sys.exit(1)
   
    def convert(self):
        print("Conversion started")
        flex_ds_instances = []
        datetime = datetime.isoformat(datetime.now())
        counter = 1

        # First, we have to build a flexible data type
        # for EVERY variant entry!
        for variant_file, mtb_filetype in self._filelist.items():
            file_path = self._tmp_dir + os.path.sep + variant_file
            print('Sample {}: Processing of file {}'.format(self._sample_code,
                variant_file))
            snv_list = SnvParser(file_path, FILETYPE_HEADER[mtb_filetype]).getSNVs()
            version = VERSIONS[mtb_filetype] 
            for snv_item in snv_list:
                ds_instance = DataSetInstance(
                    header_type=FILETYPE_HEADER[mtb_filetype],
                    snv_item=snv_item,
                    date=datetime,
                    version=version,
                    instance=counter
                )
                flex_ds_instances.append(ds_instance)
                counter += 1

        # Second, we have to build a patient data set
        # that consumes the references from the flexible
        # data set instances
        patient_ds = PatientDataSet(
            qbic_pat_id=self._patient_code,
            qbic_sample_id=self._sample_code,
            datetime=datetime,
            datasetinstance_list=flex_ds_instances
        )
        
        # Third, build the complete CentraXXDataExchange XML
        # object, that can be consumed by CentraXX
        flex_data_sets = [ds.datasetinstance() for ds in flex_ds_instances]
        self._root.Source = 'XMLIMPORT'
        effect_data = cx.EffectDataType(PatientDataSet=patient_ds.patientdataset())
        effect_data.append(flex_data_sets)
        self._root.EffectData = effect_data   
        
        root_dom = self._root.toDOM()
        root_dom.documentElement.setAttributeNS(
            xsi.uri(), 'xsi:schemaLocation',
            'http://www.kairos-med.de ../CentraXXExchange.xsd')
        root_dom.documentElement.setAttributeNS(
            xmlns.uri(), 'xmlns:xsi', xsi.uri())
        return root_dom.toprettyxml(encoding='utf-8')

    def _verify(self):
        for zipinfo in self._zip_file.infolist():
            filename = zipinfo.filename
            assigned_type = self._getfiletype(filename)
            if self._sample_code not in filename:
                raise MtbUnknownBarcode("Could not find sample_code {} in file '{}'. All"
                " files need to contain the same "
                "sample_code as the zip archive.".format(self._sample_code, filename))

            if not assigned_type:
                raise MtbUnknownFileType("Could not determine filetype "
                "according to the naming convention."
                " {} was probably not defined.".format(filename))
            self._filelist[filename] = assigned_type
        
        if len(self._filelist) != len(MtbFileType):
            raise MtbIncompleteArchive("The archive did not contain all necessary files."
            " Only found: {}".format(self._filelist.values()))
        
    def _cleanup(self):
        print(self._tmp_dir)
        os.removedirs(self._tmp_dir)

    def _getfiletype(self, filename):
        for filetype in MtbFileType:
            if filetype.value in filename:
                return filetype
        return ""
