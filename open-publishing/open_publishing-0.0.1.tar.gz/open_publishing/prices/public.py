from . import price_types

def OpenAccess():
    return price_types.OpenAccess(None, "")

def Auto():
    return price_types.Auto(None, "")

def NoPrice():
    return price_types.NoPrice(None, "")

def Manual():
    res = price_types.Manual(None, "")
    return res


