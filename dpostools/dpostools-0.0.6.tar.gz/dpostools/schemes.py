import yaml

schemes = {
    'base': yaml.load(open('yamls/basedbschema.yaml')),
    'ark': yaml.load(open('yamls/arkdbschema.yaml')),
    'oxycoin': yaml.load(open('yamls/oxycoindbschema.yaml')),
    'kapu': yaml.load(open('yamls/kapudbschema.yaml')),
}