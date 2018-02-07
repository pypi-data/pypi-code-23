'''Data Bench Transaction 

BaseTransactions are objects whose string representation is a new
random Data Bench transaction. Instatiations of TransactionTransaction
descended objects are callable, with the result being their string
representation. 

The base transaction, TransactionTransaction, is responsible for the
"header" portion of a transaction.  Subclasses are responsible for the
"payload" portion, which is expected to be an instance of
collections.OrderedDict.

'''

import time
import random
import json

from uuid import uuid4
from collections import OrderedDict

class BaseTransaction(object):
    '''Base Transacation Class
    '''

    def __init__(self, name, seed=None):
        self.name = name
        self.seed = seed or 0
        self.sep = '|'

    def __call__(self):
        '''Returns the string representation of the transaction JSON.
        '''
        return str(self)

    def __repr__(self):
        '''
        '''
        return f'{self.__class__.__name__}(name={self.name},seed={self.seed})'

    def __str__(self):
        '''String CSV-style representation of transaction data.
        '''
        return self.csv_transaction
    
    @property
    def csv_transaction(self):
        '''A string CSV-style representation of the transaction property.
        '''
        return self.sep.join(map(str,[v for v in self.transaction.values()]))

    @property
    def json_transaction(self):
        '''A string JSON representation of the transaction property.
        '''
        return json.dumps(self.transaction)
    
    @property
    def transaction(self):
        '''Dictionary of transaction items.

        Header-type items common to all transactions:

            name : string
            uuid : string uuid4
        timestamp: integer nanoseconds since Epoch
         sequence: integer monotonically increasing

        Remaining items are sourced from subclass implementations of
        the payload property.

        Raises NotImplementedError if payload property is missing.
        '''
        
        txn = OrderedDict({ 'name'     :self.name,
                            'uuid'     :self.uuid,
                            'timestamp':self.timestamp,
                            'sequence' :self.sequence })
        try:
            txn.update(self.payload)
            return txn
        except AttributeError:
            pass
        raise NotImplementedError('payload property missing')

    @property
    def uuid(self):
        '''String Universal Unique Identifier (uuid) for each transaction.
        '''
        return str(uuid4())

    @property
    def timestamp(self):
        '''Integer nanoseconds since the epoch.
        '''
        return int(time.time() * 1e9)

    @property
    def sequence(self):
        '''Monotonically increasing integer value.
        '''
        try:
            self._sequence += 1
            return self._sequence
        except AttributeError:
            pass
        self._sequence = 0
        return self._sequence

    @property
    def random(self):
        '''Random instance with a specific seed.
        '''
        try:
            return self._random
        except AttributeError:
            pass
        self._random = random.Random(self.seed)
        return self._random

    
class MarketStreamTransaction(BaseTransaction):
    '''A Data Bench Market Stream transaction source.
    '''
    def __init__(self, symbols,
                 q_min=None, q_max=None,
                 p_min=None, p_max=None,
                 seed=None):
        '''
        symbols : list of strings, symbol names
        q_min   : optional integer, defaults to 10
        q_max   : optional integer, defaults to 1001
        p_min   : optional integer, defaults to 10
        p_max   : optional integer, defaults to 1001
        seed    : optional integer

        q_min, q_max express the quanity property's bounds
        p_min, p_max express the price property's bounds
        
        '''

        super().__init__('MarketStream', seed=seed)
        self.symbols = symbols
        self.q_limits = range(q_min or 10, q_max or 1001)
        self.p_limits = range(p_min or 10, p_max or 1001)

    @property
    def payload(self):
        '''An OrderedDict with the key/value pairs specific to the
        Market Stream transaction.
        '''
        return OrderedDict({'symbol'  :self.symbol,
                            'price'   :self.price,
                            'quantity':self.quantity })

    @property
    def symbol(self):
        '''Random string chosen from the list of symbols the object
        was initialized with.
        '''
        return self.random.choice(self.symbols)

    @property
    def quantity(self):
        '''A random integer in the range of [q_min, q_max) signifying
        a number of stock units.
        '''
        return self.random.randint(self.q_limits.start, self.q_limits.stop)

    @property
    def price(self):
        '''A random float in the range of [p_min, p_max) signifying
        the price of a stock unit.
        '''
        return round(self.random.uniform(self.p_limits.start,
                                         self.p_limits.stop),
                     3)


class CustomerValuationTransaction(BaseTransaction):
    '''A Data Bench Customer Valuation transaction source.
    '''
    
    def __init__(self, base_customer_id, ncustomers, seed=None):
        '''
        base_customer_id : integer
        ncustomers       : integer
        seed             : optional integer, defaults to 0

        '''
        super().__init__('CustomerValuation', seed=seed)
        self.base_customer_id = base_customer_id
        self.ncustomers = ncustomers
        self.cid_range = range(self.base_customer_id,
                               self.base_customer_id + ncustomers)

    @property
    def payload(self):
        '''An OrderedDict with the key/value pairs specific to the
        Customer Valuation transaction.
        '''
        return OrderedDict({'customer_id':self.customer_id})

    @property
    def customer_id(self):
        '''A random integer signifying a customer identifier in
        the range of:

        (base_customer_id, base_customer_id+ncustomers].
        '''
        return self.random.randint(self.cid_range.start,
                                   self.cid_range.stop)
        
