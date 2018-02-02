from kooki.tools import write_file


def export_to_html(name, content):
    file_name = '{0}.html'.format(name)
    write_file(file_name, content)
