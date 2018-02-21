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