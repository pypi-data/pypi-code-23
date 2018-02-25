
def generate_marlin_xml()

class RunError(Exception):
    pass

def connect(input_file, output_file, release, config):
    xml_string = configdb.get(release)
    input_string =
    output_string =
    config_file, file_name = random_config_file()
    return input_xml + config_xml + output_xml

def check_xml(xml):
    # FIXME handle the
    return True



def generate(input_file, output_file, release, config):
    try:
        xml = connect(input_file, output_file, release)
        check_xml(xml)
    except:
        # FIXME handle the connection failed execption
        pass

    env = releasedb.getEnv(release)
    # FIXME handle of stderr is needed.
    ps = subprocess.Popen("Marlin {0}".format(config_file), shell=True, env=env)
