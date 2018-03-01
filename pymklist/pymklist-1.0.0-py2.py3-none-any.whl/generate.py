import glob
import os
import io
import shutil

import re

FORMAT_STRING = u'{filename:<30} {description}'
alphanum = re.compile('[\W_]+', re.UNICODE)
num = re.compile('\D', re.UNICODE)


def line_format(**kwargs):
    return FORMAT_STRING.format(**kwargs)


def do_sort(li, mode):
    def cmpkey1(row):
        return alphanum.sub('', row[mode]).lower()

    def cmpkey2(row):
        return line_format(**row)

    li.sort(key=cmpkey2)
    li.sort(key=cmpkey1)


def get_parts_lst(parts_dir, mode):
    parts = glob.glob(os.path.join(parts_dir, '*.dat'))

    parts_dict = {'_': [], '~': []}
    parts_lst = []

    for part in parts:
        filename = os.path.basename(part)
        number, _ = os.path.splitext(filename)
        with io.open(part, 'r', newline='\r\n', encoding='utf-8') as part_file:
            header = part_file.readline()
            header_description = header[2:]
            if '~Moved' in header:
                continue
            row = {'filename': filename,
                   'number': number,
                   'description': header_description}

            if '_' in header_description:
                parts_dict['_'].append(row)
            elif '~' in header_description:
                parts_dict['~'].append(row)
            else:
                parts_lst.append(row)

    do_sort(parts_lst, mode)
    do_sort(parts_dict['_'], mode)
    do_sort(parts_dict['~'], mode)

    parts_lst.extend(parts_dict['_'])
    parts_lst.extend(parts_dict['~'])

    return parts_lst


def generate_parts_lst(mode, parts_folder_path, parts_lst_path):
    if os.path.exists(parts_lst_path):
        shutil.move(parts_lst_path, parts_lst_path+'.old')

    parts_lst = get_parts_lst(parts_folder_path, mode)

    lines = [line_format(**row) for row in parts_lst]
    io.open(parts_lst_path, 'w', encoding='utf-8').writelines(lines)
