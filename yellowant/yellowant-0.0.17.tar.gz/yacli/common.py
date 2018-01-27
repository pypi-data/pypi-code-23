import json
import ConfigParser

from yacli.constants import APP_CONFIG_FILENAME, APP_FILENAME


class AppIdInvalid(Exception):
    pass

class AppDataCorrupt(Exception):
    pass

class FilePermissionError(Exception):
    pass


def save_app_config(app_id, app_invoke_name, config_file=APP_CONFIG_FILENAME):
    """Write token and host configs to a file"""
    config = ConfigParser.RawConfigParser()
    config.read(config_file)
    if not config.has_section(app_invoke_name):
        config.add_section(app_invoke_name)
    config.set(app_invoke_name, 'invoke_name', app_invoke_name)
    config.set(app_invoke_name, 'id', app_id)
    with open(config_file, 'wb') as configfile:
        config.write(configfile)

def read_app_id_from_config(app_invoke_name, config_file=APP_CONFIG_FILENAME):
    config = ConfigParser.ConfigParser()
    config.read(config_file)
    
    if not config.has_section(app_invoke_name) or not config.has_option(app_invoke_name, "id"):
        return None

    return config.get(app_invoke_name, "id")

def save_application_json(application_json, app_filename=APP_FILENAME):
    application_json.pop("client_id")
    application_json.pop("client_secret")
    with open(app_filename, "w") as outfile:
        json.dump(application_json, outfile, indent=4, sort_keys=True)
