from phreeqpython import PhreeqPython, Solution
from .chemistry import chemicals
from piwebapi import Element, Point

try:
    import influxdb
except:
    pass

lims_map = {
    "Al":(182,"AL"),
    "CH4":(226,"CH4"),
    "Cl":(164,"CL"),
    "CO2": (148, "KOOLD"),
    "EGV 20°C":(116,"GELEIDING"),
    "Fe":(146,"FE"),
    "Hardheid":(162,"HHTOT"),
    "HCO3":(150,"HCO3"),
    "K":(122,"K"),
    "Mn":(147,"MN"),
    "Na":(120,"NA"),
    "NH4":(166,"NH4"),
    "NO3":(118,"NO3"),
    "pH":(115,"PH"),
    "SO4":(715,"SO4"),
    "TOC":(405,"TOC")
}

#############################################
# Vitens phreeqpython extensions for PI A/F #
#############################################

def add_solution_af(self, path, attr_name="Waterkwaliteitsmetingen"):
    """ Create a PhreeqPython solution using data from a PI/AF tag """
    if isinstance(path, str):
        attributes = Element(path,persistence=604800).attributes[attr_name]
    else:
        attributes = path.attributes[attr_name]
    composition = {}
    charge = 0

    for name, element in attributes.children.items():
        name = name.replace(" (lab)","")

        # skip emtpy or negative values
        if isinstance(element.value, float) and element.value < 0:
            continue

        if name in chemicals:
            mg = element.value if element.units == "milligram per liter" else element.value/1000
            #print name, mg, element.units
            mmol = mg / chemicals[name][0]
            if mmol > 0:
                composition[name] = mmol
                charge += mmol * chemicals[name][1]
        elif name == "DOC":
            composition["Toc"] = element.value
        # decouple methane
        elif name == "CH4":
            composition["Mtg"] = element.value / 1000

    if charge > 0:
        composition['Nmod'] = charge
    if charge < 0:
        composition['Pmod'] = -charge

    try:
        temperatuur = attributes["Temperatuur"]
    except:
        temperatuur = 10

    return self.add_solution_simple(composition, temperatuur)

PhreeqPython.add_solution_af = add_solution_af

def write_to_influx(self, path, attribute="Waterkwaliteit Softsensor"):
    if isinstance(path, str):
        element = Element(path)
    else:
        element = path

    attributes = element.attributes[attribute]

    influx_json = []
    
    for name, attr in attributes.items():
        name = name.replace(" (lab)", "")
        if name not in lims_map:
            continue
        lims = lims_map[name]

        if name in chemicals:
            mmol = self.total(name)
            mg = chemicals[name][0] * mmol
            value = mg if attr.units == "milligram per liter" else mg * 1000
        elif name == "pH": 
            value = self.pH
        elif name[:3] == "EGV":
            value = self.egv / 10
        elif name == "Hardheid":
            value = (self.total_element('Ca') + self.total_element('Mg'))
        elif name == "TOC":
            value = self.total_element('Toc')
        elif name == "CH4":
            value = self.total_element('Mtg') * 1000
        else:
            continue
        
        influx_json.append({
            "measurement": attributes["Monsterpuntcode"].value,
            "tags": {
                "testcode": lims[0],
                "analyte": lims[1]
                },
            "fields": {
                "value": value
                }
            })

    client = influxdb.InfluxDBClient(database='slimm')
    client.write_points(influx_json)


def write_to_af(self, path, postfix, tagfilter=None):

    if isinstance(path, str):
        element = Element(path)
    else:
        element = path

    attributes = element.attributes["Waterkwaliteitsmetingen"]

    for tagname, attribute in attributes.items():
        if "(ss)" in tagname:

            if tagfilter is not None and tagfilter not in tagname:
                continue

            name = tagname.split(" ")[0]

            if name in chemicals:
                mmol = self.total(name) * 1000
                mg = chemicals[name][0] * mmol
                value = mg if attribute.units == "milligram per liter" else mg * 1000
            elif name == "pH": 
                value = self.pH
            elif name == "EGV":
                value = self.egv / 10
            elif name == "Hardheid":
                value = (self.total_element('Ca') + self.total_element('Mg')) * 1000
            elif name == "TOC":
                value = self.total_element('Toc') * 1000
            else:
                continue
                #raise NotImplementedError(name)

            path = attribute.config_string
            try:
                pipath = path.split("?")[0] + "\\" + path.split("\\")[3].split("?")[0] + postfix
                point = Point(pipath)
                point.write_value(value)
            except:
                print("write failed")
                continue

Solution.write_to_af = write_to_af
Solution.write_to_influx = write_to_influx
