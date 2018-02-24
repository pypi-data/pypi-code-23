# this module removes yaml1.1 compliant exchange of On/Off & Yes/No with True/False.
# as soon as pyyaml supports yaml1.2 this is deprecated

from yaml import load  # to be used by adriver.py and devicemanager.py
from yaml.resolver import Resolver
try:
    from yaml import CLoader as Loader, CDumper as Dumper
except ImportError:
    from yaml import Loader, Dumper

# remove resolver entries for On/Off/Yes/No
# (https://stackoverflow.com/questions/36463531/pyyaml-automatically-converting-certain-keys-to-boolean-values)
for ch in "OoYyNn":
    if len(Resolver.yaml_implicit_resolvers[ch]) == 1:
        del Resolver.yaml_implicit_resolvers[ch]
    else:
        Resolver.yaml_implicit_resolvers[ch] = [x for x in
                Resolver.yaml_implicit_resolvers[ch] if x[0] != 'tag:yaml.org,2002:bool']


def dict_deepcopy_lowercase(dict_in):
    if type(dict_in) is dict:
        dict_out = {}
        for k, v in dict_in.items():
            try:
                k = k.lower()
            except AttributeError:
                pass
            dict_out[k] = dict_deepcopy_lowercase(v)
    elif type(dict_in) is list:
        dict_out = []
        for d in dict_in:
            dict_out.append(dict_deepcopy_lowercase(d))
    else:
        dict_out = dict_in
    return dict_out
