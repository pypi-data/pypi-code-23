import clarus.services

def dsb(output=None, **params):
    return clarus.services.api_request('MIFID', 'DSB', output=output, **params)

def firds(output=None, **params):
    return clarus.services.api_request('MIFID', 'FIRDS', output=output, **params)

