import clarus.services

def defaultresources(output=None, **params):
    return clarus.services.api_request('CCP', 'DefaultResources', output=output, **params)

