"""

"""
import uuid
import subprocess

from Yuki.configDatabase import configdb
from Yuki.releaseDatabase import releasedb

class RunError(Exception):
    pass

def connect(input_file, output_file, release, config):
    execute_xml = configdb.getExecuteXml(config)
    config_xml = configdb.getConfigXml(config)
    global_xml = configdb.getGlobalXml(input_file)
    output_xml = configdb.get_output_xml(output_file, config, release)
    header_xml = configdb.getHeaderXml()
    xml = header_xml
    xml += "<marlin>\n"
    xml += execute_xml
    xml += global_xml
    xml += config_xml
    xml += output_xml
    xml += "</marlin>\n"
    return xml

def check_xml(xml):
    # FIXME handle the
    return True

def random_file():
    """ Generate a random file in /tmp, return the file and the name.
    """
    file_name = "/tmp/{0}.xml".format(uuid.uuid4().hex)
    return open(file_name, "w"), file_name

def produce(input_file, output_file, release, config):
    """ Produce the data.
    """
    xml = connect(input_file, output_file, release, config)
    try:
        print(xml)
        check_xml(xml)
    except:
        print("Failed generate xml")
        # FIXME handle the connection failed execption
        pass

    try:
        config_file, file_name = random_file()
        config_file.write(xml)
        config_file.close()
    except:
        # FIXME handle the
        pass

    env = releasedb.get_env(release)
    # FIXME handle of stderr is needed.
    try:
        ps = subprocess.Popen("Marlin {0}".format(file_name), shell=True, env=env)
        ps.wait()
    except:
        print("Fail to produce data.")

"""
from Yuki import YukiRelease
yukiRelease = YukiRelease.instance()
yukiRelease.base("")
yukiRelease.use("")

from Yuki import YukiConfiguration
yukiConfiguration = YukiConfiguration.instance()
yukiConfiguration.release("")
yukiConfiguration.base("")
yukiConfiguration.registerProcessor("", "")
"""
