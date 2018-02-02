from puer.route import route


def viewset_route(r, func, name=None):
    """
    
    :param r: (str) route
    :param func: (class|async function) handler
    :param name: route name
    :return: 
    """
    route(r, func, name)
    route("%s{id}/" % r, func, name)