from __future__ import absolute_import
print("Name is " + repr(__name__))
from .CifFile import CifFile,CifDic,CifError,CifBlock,ReadCif,ValidCifFile,ValidCifError,Validate
from .CifFile import get_number_with_esd,convert_type,validate_report
from .StarFile import StarError,ReadStar,StarList,apply_line_folding,apply_line_prefix
from .StarFile import remove_line_prefix,remove_line_folding
from .StarFile import check_stringiness
