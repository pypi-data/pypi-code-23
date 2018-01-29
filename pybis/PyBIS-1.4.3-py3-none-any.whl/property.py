from tabulate import tabulate
from texttable import Texttable
from pybis.utils import check_datatype, split_identifier, format_timestamp, is_identifier, is_permid, nvl

class PropertyHolder():

    def __init__(self, openbis_obj, type=None):
        self.__dict__['_openbis'] = openbis_obj
        self.__dict__['_property_names'] = []
        if type is not None:
            self.__dict__['_type'] = type
            for prop in type.data['propertyAssignments']:
                self._property_names.append(prop['propertyType']['code'].lower())

    def _get_terms(self, vocabulary):
        return self._openbis.get_terms(vocabulary)

    def _all_props(self):
        props = {}
        for code in self._type.codes():
            props[code] = getattr(self, code)
        return props

    def all(self):
        props = {}
        for code in self._type.codes():
            props[code] = getattr(self, code)
        return props

    def all_nonempty(self):
        props = {}
        for code in self._type.codes():
            value = getattr(self, code)
            if value is not None:
                props[code] = value

        return props

    def __getattr__(self, name):
        """ attribute syntax can be found out by
            adding an underscore at the end of the property name
        """ 
        if name.endswith('_'):
            name = name.rstrip('_')
            property_type = self._type.prop[name]['propertyType']
            if property_type['dataType'] == 'CONTROLLEDVOCABULARY':
                return self._openbis.get_terms(name)
            else:
                syntax = { property_type["label"] : property_type["dataType"]}
                if property_type["dataType"] == "TIMESTAMP":
                    syntax['syntax'] = 'YYYY-MM-DD HH:MIN:SS'
                return syntax
        else: return None

    def __setattr__(self, name, value):
        if name not in self._property_names:
            raise KeyError("No such property: '{}'".format(name)+". Allowed properties are: {}".format(self._property_names)) 
        property_type = self._type.prop[name]['propertyType']
        data_type = property_type['dataType']
        if data_type == 'CONTROLLEDVOCABULARY':
            voc = self._openbis.get_terms(name)
            if value not in voc.terms:
                raise ValueError("Value must be one of these terms: " + ", ".join(voc.terms))
        elif data_type in ('INTEGER', 'BOOLEAN', 'VARCHAR'):
            if not check_datatype(data_type, value):
                raise ValueError("Value must be of type {}".format(data_type))
        self.__dict__[name] = value

    def __dir__(self):
        return self._property_names

    def _repr_html_(self):
        def nvl(val, string=''):
            if val is None:
                return string
            elif val == 'true':
                return True
            elif val == 'false':
                return False
            return val
        html = """
            <table border="1" class="dataframe">
            <thead>
                <tr style="text-align: right;">
                <th>property</th>
                <th>value</th>
                </tr>
            </thead>
            <tbody>
        """

        for prop in self._property_names:
            html += "<tr> <td>{}</td> <td>{}</td> </tr>".format(
                prop, nvl(getattr(self, prop, ''),'')
            )

        html += """
            </tbody>
            </table>
        """
        return html

    def __repr__(self):
        def nvl(val, string=''):
            if val is None:
                return string
            elif val == 'true':
                return True
            elif val == 'false':
                return False
            return str(val)

        headers = ['property', 'value']

        lines = []
        for prop_name in self._property_names:
            lines.append([
                prop_name,
                nvl(getattr(self, prop_name, ''))
            ])
        return tabulate(lines, headers=headers)


class PropertyAssignments():
    """ holds are properties, that are assigned to an entity, eg. sample or experiment
    """

    def __init__(self, openbis_obj, data):
        self.openbis = openbis_obj
        self.data = data
        self.prop = {}
        if self.data['propertyAssignments'] is None:
            self.data['propertyAssignments'] = []
        for pa in self.data['propertyAssignments']:
            self.prop[pa['propertyType']['code'].lower()] = pa

    def __str__(self):
        """String representation of this entity type
        """
        return self.data['code']

    @property
    def code(self):
        return self.data['code']

    @property
    def description(self):
        return self.data['description']

    def __eq__(self, other):
        return str(self) == str(other)

    def __ne__(self, other):
        return str(self) != str(other)


    def codes(self):
        codes = []
        for pa in self.data['propertyAssignments']:
            codes.append(pa['propertyType']['code'].lower())
        return codes

    def _repr_html_(self):
        html = """
<p>{}: <b>{}</b>
<p>description: {}</p>
        """.format(
            self.data['@type'].split('.')[-1],
            self.data['code'], 
            self.data['description']
        )
        if 'autoGeneratedCode' in self.data:
            html += "<p>Code autogenerated: {}</p>".format(
                self.data['autoGeneratedCode'])

        html += """
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th>property</th>
      <th>label</th>
      <th>description</th>
      <th>dataType</th>
      <th>mandatory</th>
    </tr>
  </thead>
  <tbody>
        """

        for pa in self.data['propertyAssignments']:
            html += "<tr> <th>{}</th> <td>{}</td> <td>{}</td> <td>{}</td> <td>{}</td> </tr>".format(
                pa['propertyType']['code'].lower(),    
                pa['propertyType']['label'],    
                pa['propertyType']['description'],    
                pa['propertyType']['dataType'],    
                pa['mandatory']
            )

        html += """
            </tbody>
            </table>
        """
        return html

    def __repr__(self):
        title = """
{}: {}
description: {}""".format (
            self.data['@type'].split('.')[-1],
            self.data['code'], 
            self.data['description']
        )

        table = Texttable()
        table.set_deco(Texttable.HEADER)

        headers = ['code', 'label', 'description', 'dataType', 'mandatory']

        lines = []
        lines.append(headers)
        for pa in self.data['propertyAssignments']:
            lines.append([
                pa['propertyType']['code'].lower(),    
                pa['propertyType']['label'],    
                pa['propertyType']['description'],    
                pa['propertyType']['dataType'],    
                pa['mandatory']
            ])
        table.add_rows(lines)
        table.set_cols_width([28,28,28,28,9])
        table.set_cols_align(['l','l','l','l','l'])
        return title + "\n\n" + table.draw()
