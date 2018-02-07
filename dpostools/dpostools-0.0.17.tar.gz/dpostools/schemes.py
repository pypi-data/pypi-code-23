import yaml
import pkg_resources

resource_package = __name__

base_resource_path = '/'.join(('yamls', 'basedbschema.yaml'))
base = pkg_resources.resource_filename(__name__, base_resource_path)

ark_resource_path = '/'.join(('yamls', 'arkdbschema.yaml'))
ark = pkg_resources.resource_filename(resource_package, ark_resource_path)

oxy_resource_path = '/'.join(('yamls', 'oxycoindbschema.yaml'))
oxy = pkg_resources.resource_filename(resource_package, oxy_resource_path)

kapu_resource_path = '/'.join(('yamls', 'kapudbschema.yaml'))
kapu = pkg_resources.resource_filename(resource_package, kapu_resource_path)


schemes = {
    'base': yaml.load(open(base)),
    'ark': yaml.load(open(ark)),
    'oxycoin': yaml.load(open(oxy)),
    'kapu': yaml.load(open(kapu)),
}