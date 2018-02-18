import re
import models

models_to_match = [
        models.Prefix
    ,   models.EditDevice
    ,   models.EditSymbol
    ,   models.Pin
    ,   models.Wire
    ,   models.Layer
    ,   models.Connect
    ,   models.Description
    ,   models.Attribute
    ,   models.EditPackage
    ,   models.Package
    ,   models.Add
    ,   models.Package
    ,   models.Smd
    ,   models.Grid
    ,   models.Set
    ]

class Parser(object):
    current_obj = None

    def __init__(self):
        self.context = {
                'layer': 0
            ,   'grid': None 
            ,   'symbols': {}
            ,   'devices': {}
            ,   'packages': {}
            ,   'settings': {}
            }

    def handle_line(self, line):
        line = line.strip()
    
        if len(line) == 0 or line.startswith("#"):
            return True # Skip empty lines and commands.

        # Ask each model if it matches the line we're considering. If it does,
        # it will return an instance of itself.
        for model in models_to_match:
            match = re.compile(model.regex).match(line)
            if match:
                obj = model(self.context, **match.groupdict())
                break
            else:
                obj = None

        if not obj:
            # No class wanted to claim a match for this line, we can't
            # handle this.
            return False
        
        # These commands set up a new Symbol, Device or Package.
        if isinstance(obj, models.EditSymbol):
            self.context['symbols'][obj.name] = obj
            self.current_obj = obj
        elif isinstance(obj, models.EditDevice):
            self.context['devices'][obj.name] = obj
            self.current_obj = obj
        elif isinstance(obj, models.EditPackage):
            self.context['packages'][obj.name] = obj
            self.current_obj = obj

        # These commands modify the global context, so we can just handle them
        # here.
        elif isinstance(obj, models.Layer):
            self.context['layer'] = obj.num
        elif isinstance(obj, models.Grid):
            self.context['grid'] = obj.value
        elif isinstance(obj, models.Set):
            self.context['settings'][obj.key] = obj.value

        elif self.current_obj is not None:
            # This is a command inside a large block like a Package, Symbol or
            # Device, so that model should be able to handle this.
            self.current_obj.handle(obj)

        return True
 
