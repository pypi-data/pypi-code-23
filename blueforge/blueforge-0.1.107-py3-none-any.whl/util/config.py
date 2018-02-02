import json


class config:
    """ The config for getting config information """

    @classmethod
    def _from_parsed_json_keyfile(cls, raw_json):
        """ This is for parsing json data from file
            Args:
                raw_json: Raw Json Data """
        return raw_json

    @classmethod
    def from_json_config(cls, filename):
        with open(filename, 'r') as file_obj:
            config_data = json.load(file_obj)

        return cls._from_parsed_json_keyfile(raw_json=config_data)
