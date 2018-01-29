import xml.etree.ElementTree as ET
from io import StringIO


class XMLHelper:
    def __init__(self, encoded_xml):
        self._namespaces = (
            dict(map(lambda el: el[1],
                     ET.iterparse(StringIO(encoded_xml),
                                  events=['start-ns']))))

        self._document = ET.parse(StringIO(encoded_xml))

        for namespace in self._namespaces.items():
            ET.register_namespace(namespace[0], namespace[1])

    @property
    def root(self):
        return self._document.getroot()

    def namespace(self, shortname):
        return self._namespaces.get(shortname, None)

    def deep_copy(self):
        return XMLHelper(self.serialize(self.root).decode('utf-8'))

    @property
    def default_namespace(self):
        return self._namespaces['']

    def attribute_fullname(self, name, namespace=None):
        return ('{%s}%s' % (self.namespace(namespace), name)
                if namespace is not None
                else name)

    def get_attribute(self, node, name, namespace=None):
        try:
            return node.attrib[self.attribute_fullname(name, namespace)]
        except KeyError:
            return None

    def set_attribute(self, node, name, value, namespace=None):
        node.attrib[self.attribute_fullname(name, namespace)] = value

    def del_attribute(self, node, name, namespace=None):
        del node.attrib[self.attribute_fullname(name, namespace)]

    def has_attribute(self, node, name, namespace=None):
        return self.attribute_fullname(name, namespace) in node.attrib

    def serialize(self, node):
        return ET.tostring(node)
