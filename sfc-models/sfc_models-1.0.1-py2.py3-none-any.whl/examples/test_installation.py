
import os
from pkg_resources import resource_string


def install(target_dir):
    file_list = resource_string('sfc_models.examples', 'scripts/script_list.txt')
    for fname in file_list.split('\n'):
        fname = fname.strip()
        if len(fname) == 0:
            continue
        full_name = os.path.join(target_dir, fname)
        contents = resource_string('sfc_models.examples', 'scripts/' + fname)
        with open(full_name, 'w') as f:
            f.write(contents)

