from open_publishing.order_fulfillment import OrderFulfillment

class OrderFulfillments(object):
    def __init__(self,
                 ctx):
        self._ctx = ctx
        self._refs = set() #TODO: Consider using weakref 
        
    def load(self,
             guid = None,
             order_id = None,
             fetch = True):
        if guid is not None and order_id is None:
            order_id = OrderFulfillment.id_from_guid(guid)
        elif order_id is not None and guid is None:
            order_id = order_id
        else:
            raise TypeError('guid or order_id should be specified')
        
        order_fulfillment = OrderFulfillment(self._ctx,
                                             order_id)
        if fetch:
            order_fulfillment._fetch(['*'])
        return order_fulfillment
        

    def flush(self):
        refs = self._refs.copy()
        for order_fulfillment in refs:
            order_fulfillment.flush()
        self._refs = set()

    def _add_to_changed(self,
                        database_object):
        self._refs.add(database_object)

    def _remove_from_changed(self,
                             database_object):
        if database_object in self._refs:
            self._refs.remove(database_object)


