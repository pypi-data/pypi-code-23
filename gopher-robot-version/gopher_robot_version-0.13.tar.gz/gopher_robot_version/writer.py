





def prepare_dict(dict_name_version):
    """
    Transform dict[name] = version into list["name  version", ...]
    :return:
    """
    list_name_version = []
    space_size = 70
    for name, version in dict_name_version.iteritems():
        str = name + (space_size - len(name)) * " " + version
        list_name_version.append(str)
    list_name_version.sort()
    return list_name_version

def dict_to_str(dict_name_version, identifier):
    final_str = ""
    list_name_version = prepare_dict(dict_name_version)
    final_str += identifier + '\n'
    final_str += '-' * 80 + '\n'
    for line in list_name_version:
        final_str += line + '\n'
    final_str += '\n' * 4
    return final_str

def write_to_file(filename, data):
    fp = open(filename, "w+")
    fp.write(data)
    fp.close()
