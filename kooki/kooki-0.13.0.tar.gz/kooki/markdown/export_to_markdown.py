from kooki.tools import write_file


def export_to_markdown(name, content):
    file_name = '{0}.md'.format(name)
    write_file(file_name, content)
