"""Data-set instance represents a CentraXX FlexibleDataSetInstance
type for the patient import"""

import uuid
import datetime

class DataSetInstance():

    def __init__(self, header_type, snv_item, date, version, instance):
        """DataSetInstance object
        _header_type: The header type of enum mtbparser.snv_utils.SSnvHeader, ...
        _snv_item: An entry of class mtbparser.snv_items.SNVItems()
        _date: ISO 8601 formatted timestamp
        _version: A version tag as string
        _instance: An incremental integer for the instance
        _reference: A random uuid4 id for cross referencing
        """
        self._header_type = header_type
        self._snv_item = snv_item
        self._date = date
        self._version = version
        self._instance = instance
        self._reference = str(uuid.uuid4())

    def reference(self):
        """Return the uuid4 reference id"""
        return self._reference

    def datasetinstance(self):
        """Return a FlexibleDataSetInstance object"""
        timestamp = datetime.datetime.now().isoformat(timespec='milliseconds')
        flex_dataset = cx.FlexibleDataSetInstanceType()
        flex_dataset.FlexibleDataSetTypeRef = self._version
        flex_dataset.InstanceName = '{}_increment{}_{}'.format(
            self._version, instance, timestamp)
        flex_dataset.DateType = cx.DateType(Date=timestamp, Precision='EXACT')
        snv_columns = []
        for key, value in self._snv_item:
            value_type = self._valuetypefromfield(key)
            snv_columns.append(value_type(FlexibleValueTypeRef=cx_utils.CV_PREFIX + key,
                Value=value))
        flex_dataset.append(snv_columns)
        return flex_dataset

    def _valuetypefromfield(self, field):
        """Determine value type from a field"""
        if field in ['tumor_content', 'allele_frequency_tumor', 'coverage']:
            return cx.FlexibleDecimalDataType()
        if field in ['genotype', 'mutational_load', 'ref', 'effects', 'chromosomes']:
            return cx.FlexibleEnumerationDataType()
        if field in ['start', 'end']:
            return cx.FlexibleIntegerDataType()
        return cx.FlexibleStringDataType()
        