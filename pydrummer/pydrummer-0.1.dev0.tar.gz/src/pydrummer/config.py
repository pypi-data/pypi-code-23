from pkg_resources import resource_string, resource_listdir, resource_filename
import os.path

"""Add your drumkits here.

DRUMKITS maps the name of a drumkit to its samples directory.
"""
DRUMKITS = {
    'tr808': 'samples/808',
}

"""Sample wave files for each drumkit provided in DRUMKITS.

e.g. To access the 'kick' sample in the 'tr808' drumkit:
kick_filepath = SAMPLES['tr808']['kick']
"""
SAMPLES = {
    name: {
        os.path.splitext(sample)[0]: resource_filename(__name__, os.path.join(path, sample))
        for sample in resource_listdir(__name__, path) if sample.endswith('.wav')
    }
    for name, path in DRUMKITS.items()
}