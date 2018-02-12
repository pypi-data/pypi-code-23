class SNVItem():

    def __init__(self, **info):
        self._snv_info = self._format_dict(info)

    def _format_dict(self, info_dict):
        """Replaces empty content with 'NA's"""
        for key, value in info_dict.items():
            if not value:
                info_dict[key] = "NA"
        return info_dict

    def get_snv_info(self, attribute):
        information = ""
        try:
            information = self._snv_info[attribute]
        except KeyError:
            pass
        return information
    
