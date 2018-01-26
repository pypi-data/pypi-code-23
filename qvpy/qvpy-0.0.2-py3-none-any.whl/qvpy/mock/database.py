# -*- coding: utf-8 -*-

### imports ###################################################################
import logging


###############################################################################
class FeatureDB:
    def __init__(self):
        pass

    def Delete(self):
        return 1

    def DeleteAll(self):
        pass

    def Item(self, **kwargs):
        item = Item(**kwargs)
        return item


###############################################################################
class Item:
    def __init__(self, **kwargs):
        a = 0
        an = 0
        cr = 0
        d = 0
        z = 0

        for key, value in kwargs.items():
            if key == 'Tag':
                if value == "FokuspunktKante":
                    z = 3.21
                elif value == "FokuspunktKanteMerkmal":
                    z = 3.14
                elif value == 'Kodierbohrung1':
                    d = 2.64
                elif value == 'Kodierbohrung2':
                    d = 2.12
                elif value == 'NotchPos':
                    a = 45
                elif value == 'Aussenkreis':
                    d = 150.
                    cr = 0.01
                else:
                    logging.warning('unknown tag: %s', value)
            else:
                logging.warning('unknown keyword: %s', key)

        self.A = Value(a)
        self.AN = Value(an)
        self.CR = Value(cr)
        self.D = Value(d)
        self.Z = Value(z)


###############################################################################
class PtBufDB:
    def __init__(self):
        pass

    def DeleteAll(self):
        pass


###############################################################################
class TolDB:
    def __init__(self):
        pass

    def DeleteAll(self):
        pass


###############################################################################
class Value:
    def __init__(self, value):
        self.Actual = value
