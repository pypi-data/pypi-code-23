from .mtbparser_exception import MTBParserException
from .snv_item import SNVItem

class SnvParser:
    """
    A parser class for somatic SNVs and small indels
    as part of the Molecular Tumor Board data
    provisioning in tumor diagnostics.
    Please check the documentation of this module in order
    to find out the exact file format specification.
    """
    def __init__(self, snv_file, snv_enum_type):
        self._header_to_column_mapping = {}
        self._path_to_snv_file = snv_file
        self._snv_list = []
        self._snv_enum = snv_enum_type

        with open(snv_file, "r", encoding="utf-8") as fh:
            lines = fh.readlines()
        if not lines:
            raise MTBParserException("Parsing failed: File was empty!")
        header = lines[0]
        self._parse_header(header)
        self._parse_content(lines)

    def _parse_header(self, header_string):
        """
        Parses the header and determines the column type
        and its column index.
        """
        header_content = header_string.strip().split('\t')
        if len(header_content) != self._snv_enum.HEADER_LEN.value:
            raise MTBParserException(
                "Only {} header columns found, {} expected!"
                .format(len(header_content), self._snv_enum.HEADER_LEN.value))
        counter = 0
        for column in header_content:
            for enum_type in self._snv_enum:
                if column == enum_type.value:
                    self._header_to_column_mapping[enum_type.name] = counter
                    continue
            counter+=1

        if len(self._header_to_column_mapping) != self._snv_enum.HEADER_LEN.value:
            debug_string = self._header_to_column_mapping.keys()
            raise MTBParserException("Parsing incomplete: Not all columns have been "
                    "matched to speficied column types. Identified {} columns, but expected {}. {}"
                    .format(len(self._header_to_column_mapping), self._snv_enum.HEADER_LEN.value, debug_string))

    def _parse_content(self, snv_entries):
        """
        Parses SNV entries to SNVItems, objects
        representing the content for every entry, that
        can be used for further processing.
        """
        if len(snv_entries) == 1:
            return
        for line in snv_entries[1:]:
            info_dict = self._map_info_to_col(line)
            self._snv_list.append(SNVItem(**info_dict))
    
    def _map_info_to_col(self, line):
        line_content = line.rstrip().split("\t")
        tmp_info_dict = {}
        try:
            for column, index in self._header_to_column_mapping.items():
                tmp_info_dict[column] = line_content[index]
        except IndexError:
            raise MTBParserException("Parsing of an SNV element failed, because the "
                        "value for {} could not be determined.".format(column))
        return tmp_info_dict

    def getSNVs(self):
        """
        Retrieve all parsed SNVItems.
        """
        return self._snv_list
