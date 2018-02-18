class Pin(object):
    regex = "^Pin '(?P<name>[A-Za-z0-9_-]+)' "\
        "(?P<pintype>[A-Za-z/]+) "\
        "(?P<unknown1>[A-Za-z]+) "\
        "(?P<unknown2>[A-Za-z]+) "\
        "R(?P<rotation>([0-9]+)) "\
        "(?P<unknown3>[^ ]+) "\
        "(?P<unknown4>[^ ]+) "\
        "\((?P<pos_x>[0-9-\.]+) (?P<pos_y>[0-9-\.]+)\)"\
        ";$"
    
    device = None
    device_pin_number = None
    symbol = None

    def __init__(self, context, **kwargs):
        self.context = context
        self.name = kwargs['name']
        self.pintype = kwargs['pintype']
        self.rotation = float(kwargs['rotation'])
        self.pos_x = float(kwargs['pos_x'])
        self.pos_y = float(kwargs['pos_y'])
    
    def __repr__(self):
        return "<Pin %s type=%s rotation=%d position=%d,%d device=%s.%s>" % (
                self.name
            ,   self.pintype
            ,   self.rotation
            ,   self.pos_x
            ,   self.pos_y
            ,   self.device.name
            ,   self.device_pin_number
            )


class Layer(object):
    regex = "^Layer (?P<layer>[0-9]+);$"

    def __init__(self, context, **kwargs):
        self.context = context
        self.num = kwargs['layer']


class Grid(object):
    regex = "^Grid (?P<grid>.+);$"

    def __init__(self, context, **kwargs):
        self.context = context
        self.value = kwargs['grid']


class Set(object):
    regex = "^Set (?P<key>[^ ]+) (?P<value>.+);$"

    def __init__(self, context, **kwargs):
        self.context = context
        self.key = kwargs['key']
        self.value = kwargs['value']


class Wire(object):
    regex = "^Wire (?P<size>[0-9]+) \((?P<x1>[0-9-\.]+) (?P<y1>[0-9-\.]+)\) "\
        "\((?P<x2>[0-9-\.]+) (?P<y2>[0-9-\.]+)\);"
    
    def __init__(self, context, **kwargs):
        self.context = context
        self.size = kwargs['size']
        self.x1 = kwargs['x1']
        self.y1 = kwargs['y1']
        self.x2 = kwargs['x2']
        self.y2 = kwargs['y2']
        self.layer = context['layer']


class EditSymbol(object):
    regex = "^Edit '(?P<name>[^\.]+)\.sym';$"

    def __init__(self, context, **kwargs):
        self.context = context
        self.pins = {}
        self.name = kwargs['name']
        self.lines = []

    def handle(self, obj):
        if isinstance(obj, Pin):
            # Establish a bi-directional map between this Pin and the
            # current Symbol
            self.pins[obj.name] = obj
            obj.symbol = self
            return
        elif isinstance(obj, Wire):
            self.lines.append(obj)
            return

    def __repr__(self):
        return "<Symbol %s, %d pins, %d lines>" % (self.name, len(self.pins), len(self.lines))


class EditDevice(object):
    regex = "^Edit '(?P<partname>[^\.]+)\.dev';$"

    def __init__(self, context, **kwargs):
        self.context = context
        self.name = kwargs['partname']
        self.attributes = {}
        self.prefix = None
        self.package = None
        self.description = ""
        self.symbols = {}
        self.pins = {}

    def __repr__(self):
        return "<Device %s>" % self.name

    def handle(self, obj):
        if isinstance(obj, Prefix):
            self.prefix = obj
        elif isinstance(obj, Add):
            self.symbols[obj.prefix] = obj
        elif isinstance(obj, Package):
            # TODO look up package and get the real reference.
            self.package = self.context['packages'][obj.name]
        elif isinstance(obj, Attribute):
            self.attributes[obj.key] = obj.value
        elif isinstance(obj, Description):
            self.description = obj
        elif isinstance(obj, Connect):
            # Establish a bi-directional reference between this pin number
            # on this device and the pin name on the symbol referenced by
            # this pin device mapping.

            # Resolve the prefix in the Connect pin name to the Symbol from
            # the Add command.
            partname = self.symbols[obj.prefix].name

            # Tell the Symbol's Pin that it's mapped on this Device as this pin number
            symbol = self.context['symbols'][partname]
            pin = symbol.pins[obj.name]
            pin.device = self
            pin.device_pin_number = obj.number

            # Map this pin number to the right Symbol Pin
            self.pins[obj.number] = pin

class Prefix(object):
    regex = "^Prefix '(?P<prefix>[^\.]+)';$"
    
    def __init__(self, context, **kwargs):
        self.context = context
        self.prefix = kwargs['prefix']


class Add(object):
    regex = "^Add (?P<partname>[^ ]+) '(?P<prefix>[^']+)' "\
        "(?P<unknown1>[^ ]+) + (?P<unknown2>[^ ]+) +"\
        "\((?P<x>[0-9-\.]+) (?P<y>[0-9-\.]+)\);$"
    
    def __init__(self, context, **kwargs):
        self.context = context
        self.name = kwargs['partname']
        self.prefix = kwargs['prefix']

        # TODO maybe map 'name' back to the symbol object? Don't have a
        # reference to the already-loaded blocks yet.


class Package(object):
    regex = "^Package '(?P<name>[^']+)';$"
    
    def __init__(self, context, **kwargs):
        self.context = context
        self.name = kwargs['name']


class Attribute(object):
    regex = "^Attribute (?P<key>[^ ]+) '(?P<value>[^']+)';$"
    
    def __init__(self, context, **kwargs):
        self.context = context
        self.key = kwargs['key']
        self.value = kwargs['value']


class Description(object):
    regex = "^Description '(?P<value>[^']+)';$"
    
    def __init__(self, context, **kwargs):
        self.context = context
        self.value = kwargs['value']


class Connect(object):
    regex = "^Connect '(?P<prefix>[^\.]+)\.(?P<pin_name>[^']+)' '(?P<pin_number>[^']+)';$"
    
    def __init__(self, context, **kwargs):
        self.context = context
        self.prefix = kwargs['prefix']
        self.name = kwargs['pin_name']
        self.number = kwargs['pin_number']


class EditPackage(object):
    regex = "^Edit '(?P<name>[^\.]+)\.pac';$"
    
    def __init__(self, context, **kwargs):
        self.context = context
        self.name = kwargs['name']
        self.lines = []
        self.smd_pads = {}
    
    def __repr__(self):
        return "<Package %s lines=%d smd_pads=%s>" % (self.name, 
        len(self.lines), len(self.smd_pads))

    def handle(self, obj):
        if isinstance(obj, Wire):
            self.lines.append(obj)
        elif isinstance(obj, Smd):
            self.smd_pads[obj.name] = obj

        # TODO support Pads


class Smd(object):
    regex = "^Smd '(?P<name>[^']+)' (?P<dx>[^ ]+) (?P<dy>[^ ]+) "\
    "(?P<unknown1>[^ ]+) R(?P<rotation>[^ ]+) "\
    "\((?P<x>[0-9-\.]+) (?P<y>[0-9-\.]+)\);$"
    
    def __init__(self, context, **kwargs):
        self.context = context
        self.name = kwargs['name']
        self.width = float(kwargs['dx'])
        self.height = float(kwargs['dy'])
        self.rotation = float(kwargs['rotation'])
        self.x = float(kwargs['x'])
        self.y = float(kwargs['y'])
        self.layer = context['layer']

    def __repr__(self):
        return "<Smd %s x=%d y=%d width=%d height=%d rotation=%d>" % (
            self.name, self.width, self.height, self.rotation, 
            self.x, self.y)

