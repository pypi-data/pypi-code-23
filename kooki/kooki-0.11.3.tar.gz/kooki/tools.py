from codecs import open
import yaml
import os


def get_extension(file_name):
    tmp = file_name.split('.')
    if len(tmp) > 1:
        return tmp[-1]
    else:
        return ''


def get_front_matter(content):
    first_line = content.split('\n', 1)[0]
    front_matter = {}

    if first_line == '---':
        content_splitted = content.split('---\n')
        if len(content_splitted) >= 3:
            metadata_content = content_splitted[1]
            content = '---\n'.join(content_splitted[2:])
            front_matter = yaml.load(metadata_content)
        else:
            content = '---\n'.join(content_splitted)

    return front_matter, content


def read_file(file_name):
    try:
        stream = open(file_name, 'r', encoding='utf8')
        content = stream.read()
    except IOError as e:
        raise RuntimeError('No such file: \'{0}\''.format(file_name))
    else:
        stream.close()
        return content


def write_file(file_name, content):
    path = '/'.join(file_name.split('/')[:-1])
    if path != '' and not os.path.isdir(path):
        os.makedirs(path)

    stream = open(file_name, 'w', encoding='utf8')
    stream.write(content)
    stream.close()
    return content
