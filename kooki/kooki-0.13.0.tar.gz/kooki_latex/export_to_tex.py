from kooki.tools import write_file


def export_to_tex(name, content):
    file_name = '{0}.tex'.format(name)
    write_file(file_name, content)
