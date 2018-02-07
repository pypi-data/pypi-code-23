# -*- coding: utf-8 -*-
'''
'''

from faker.providers import BaseProvider
from collections import OrderedDict
import functools


class DataProvider(BaseProvider):
    '''
    '''
    _n_customers = 1000
    _base_seed = 0
    
    _customer_keys = [
        'C_ID', 'C_TAX_ID', 'C_ST_ID',
        'C_L_NAME', 'C_F_NAME', 'C_M_NAME',
        'C_GENDER', 'C_TIER', 'C_DOB', 'C_AD_ID',
        'C_COUNTRY_1', 'C_AREA_1', 'C_LOCAL_1', 'C_EXT_1',
        'C_COUNTRY_2', 'C_AREA_2', 'C_LOCAL_2', 'C_EXT_2',
        'C_COUNTRY_3', 'C_AREA_3', 'C_LOCAL_3', 'C_EXT_3',
        'C_EMAIL_1', 'C_EMAIL_2',
    ]
    _customer_account_keys = [
        'CA_C_ID', 'CA_ID', 'CA_TAX_ID',
        'CA_B_ID', 'CA_NAME', 'CA_BAL',
        'CA_L_NAME', 'CA_F_NAME', 'CA_M_NAME',
    ]
    _exchange_keys = [
        'EX_ID', 'EX_NAME', 'EX_NUM_SYMBOLS',
        'EX_OPEN', 'EX_CLOSE', 'EX_DESC', 'EX_AD_ID',
    ]
    _security_keys = [
        'S_SYMBOL', 'S_ISSUE', 'S_ST_ID', 'S_NAME', 
        'S_EX_ID', 'S_CO_ID', 'S_NUM_OUT', 'S_START_DATE', 
        'S_EXCH_DATE', 'S_PE', 'S_52WK_HIGH', 'S_52WK_HIGH_DATE', 
        'S_52WK_LOW', 'S_52WK_LOW_DATE', 'S_DIVIDEND', 'S_YIELD',
    ]
    _holding_keys = [
        'H_T_ID', 'H_CA_ID', 'H_S_SYMBOL',
        'H_DTS', 'H_PRICE', 'H_QUANTITY', 
    ]
    _last_trade_keys = [ 
        'LT_S_SYMBOL', 'LT_DTS', 'LT_PRICE',
        'LT_OPEN_PRICE', 'LT_VOL',
    ]
    _company_keys = [
        'CO_ID', 'CO_NAME', 'CO_SYMBOL',              
        'CO_EX_ID', 'CO_EX_NAME',
    ]    
    account_name_labels = [
        '401(K)',
        'Business Account',
        'College Fund',
        'Custodial Account',
        'Emergency Expenses',
        'Family Trust',
        'Flexible Spending',
        'Health Savings',
        'Healthcare Fund',
        'House Money',
        'IRA-SEP',
        'Individual Account',
        'Joint Account',
        'New Car',
        'Non-Taxable Trust',
        'Pension Account',
        'Play Money',
        'Retirement Fund',
        'Rollover IRA',
        'Roth 401(K)',
        'Roth IRA',
        'Savings Account',
        'Traditional IRA',
        'Vacation Account'
    ]
    exchange_names = {
        'AMEX':   0.25,
        'NASDAQ': 0.25,
        'NYSE':   0.25,
        'PCX':    0.25
    }
    exchange_ids = {
        'AMEX':   'EX00000001',
        'NASDAQ': 'EX00000002',
        'NYSE':   'EX00000003',
        'PCX':    'EX00000004'
    }
    issue_names = {
        'COMMON': 0.90,
        'PREF_A': 0.01,
        'PREF_B': 0.02,
        'PREF_C': 0.03,
        'PREF_D': 0.05,
    }
    symbol_formats = {
        '?':     0.01,
        '??':    0.01,
        '???':   0.22,
        '????':  0.75,
        '?????': 0.01,
    }
    symbol_letters = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
    tax_id_formats = {
        '##-#######':  0.5,
        '###-##-####': 0.5
    }
    trading_tiers = {
        'A': .20,
        'B': .60,
        'C': .20,
    }
    accounts_per_tier = {
        'A': range(1,4),
        'B': range(2,8),
        'C': range(5,10)
    }
        
    @classmethod
    def scaled(cls, customers=1000, base_seed=0):
        '''
        '''
        attrs = {
            '_n_customers':customers,
            '_base_seed':base_seed,
        }
        return type('ScaledDataProvider', (cls,), attrs)

    def __init__(self, generator, nb_customers=None, seed=None):
        '''
        '''
        super().__init__(generator)
        self.n_customers = (nb_customers or self._n_customers)
        self.n_companies = int(((self.n_customers) / 1000) * 500)
        self.base_seed = seed or self._base_seed
        self._states = {}

    def _seed_instance(self, seed):
        '''
        '''
        self.generator.seed_instance(seed + self.base_seed)

    @property
    def customer_ids(self):
        '''
        A list of string customer identifiers with prefix 'CU-'.
        The list is DataProvider.n_customers in length.
        '''
        try:
            return self._customer_ids
        except AttributeError:
            pass
        self._customer_ids = []
        for n in range(self.n_customers):
            self._seed_instance(n)
            self._customer_ids.append(self.identifier(prefix='CU-'))
        return self._customer_ids
    
    def customers(self):
        '''A generator that steps thru customer_ids in ascending order and
        yields each customer.
        '''
        for idx in range(self.n_customers):
            yield self.customer(index=idx)

    @functools.lru_cache(maxsize=None)
    def customer_accounts(self):
        ''' A list of customer
        '''
        accounts = []
        for n, customer in enumerate(self.customers()):
            self._seed_instance(n)
            accounts.extend(self._customer_accounts(customer))
        return accounts
    
    @property
    def company_ids(self):
        '''
        '''
        try:
            return self._company_ids
        except AttributeError:
            pass
        self._company_ids = []
        for n in range(self.n_companies):
            self._seed_instance(n)
            self._company_ids.append(self.identifier(prefix='CO-'))
        return self._company_ids


    def companies(self):
        '''A list of all companies.
        '''
        return [self.Company(company_id=cid) for cid in self.company_ids]

    def securities(self):
        '''
        '''
        l = []
        for n, cid in enumerate(self.company_ids):
            l.extend(self.securitiesForCompany(index=n))
        return l

    @property
    def exchanges(self):
        '''
        '''
        try:
            return self._exchanges
        except AttributeError:
            pass
        self._exchanges = []

        for n, ex_name in enumerate(self.exchange_names):
            self._seed_instance(n)
            self._exchanges.append(self.exchange(ex_name))
        return self._exchanges


    def tax_id(self):
        '''A US tax identfier in either EIN or SSN format.

        Associated with a customer.
        '''
        tax_id_fmt = self.random_element(self.tax_id_formats)
        return self.numerify(tax_id_fmt)

    def identifier(self, prefix=None, count=16):
        '''A string numeric identifier with optional string prefix.
        '''
        digit = '#'
        prefix = (prefix or '')
        return self.numerify(f'{prefix}{digit * count}')

    def trading_tier(self):
        '''A customer's trading tier.
        '''
        return self.random_element(self.trading_tiers)

    def date_of_birth(self, low=18, hi=110):
        '''Date Of Birth
        '''
        age = self.generator.random.randrange(low, hi)
        return self.generator.past_datetime(f'-{age}y').isoformat()

    def gendered_name_tuple(self, gender=None):
        '''Returns a tuple: (gender, first, middle_initital, last)
        '''
        gender = (gender or self.random_element({'F': 0.5, 'M': 0.5}))
        if gender == 'F':
            f, m, l = (self.generator.first_name_female(),
                       self.generator.first_name_female()[0],
                       self.generator.last_name_female())
        else:
            f, m, l = (self.generator.first_name_male(),
                       self.generator.first_name_male()[0],
                       self.generator.last_name_male())
        return (gender, f, m, l)


    @functools.lru_cache(maxsize=None)
    def customer(self, customer_id=None, index=None):
        '''A customer record in an OrderedDict.

        :param: customer_id - optional string
        :param: index       - optional integer

        If a valid customer_id is provided, returns that customer's record.
        If an index is provided, returns the referenced customer's record

        If both customer_id and index are provided, index takes precedence.

        If index is out of bounds IndexError is raised.
        If customer_id does not match a customer, KeyError is raised.
        '''

        if index is None:
            customer_id = (customer_id or
                           self.random.element(self.customer_ids))
            n = self.customer_ids.index(customer_id)
        else:
            n = index
            customer_id = self.customer_ids[n]
            
        self._seed_instance(n)
        
        gender, f_name, m_initial, l_name = self.gendered_name_tuple()

        values = [
            customer_id, self.tax_id(),
            self.identifier(prefix='ST'),
            l_name, f_name, m_initial, gender,
            self.trading_tier(), self.date_of_birth(),
            self.generator.address(),
            self.numerify('+!'), self.numerify('###'),
            self.numerify('###-####'), self.numerify('####'),
            self.numerify('+!'), self.numerify('###'),
            self.numerify('###-####'), self.numerify('####'),
            self.numerify('+!'), self.numerify('###'),
            self.numerify('###-####'), self.numerify('####'),
            self.generator.email(),
            self.generator.email()
        ]
        
        return OrderedDict(zip(self._customer_keys, values))

    def customer_account_name(self, customer=None):
        '''A customer account name string.
        '''
        customer = (customer or self.customer())
        label = self.generator.random_element(self.account_name_labels)
        return ' '.join([customer['C_F_NAME'],
                         customer['C_L_NAME'],
                         label])

    def cash(self):
        '''A positive floating point number with a two digit mantissa.
        '''
        return self.generator.pyfloat(right_digits=2, positive=True)

    def _customer_accounts(self, customer):
        '''
        '''
        tier = customer['C_TIER']
        n = self.random_int(min=self.accounts_per_tier[tier].start,
                            max=self.accounts_per_tier[tier].stop)
        return [self.customer_account(customer) for _ in range(n)]

    def customer_account(self, customer):
        '''A customer account record in an OrderedDict.
        '''
        values = [
            customer['C_ID'],
            self.identifier(prefix='CA'),
            customer['C_TAX_ID'],
            self.identifier(prefix='B'),
            self.customer_account_name(customer=customer),
            self.cash(),
            customer['C_L_NAME'],
            customer['C_F_NAME'],
            customer['C_M_NAME'],
        ]
        return OrderedDict(zip(self._customer_account_keys, values))

    def symbol(self):
        '''A company ticker symbol.
        '''
        fmt = self.random_element(self.symbol_formats)
        return self.lexify(text=fmt, letters=self.symbol_letters)

    def exchange(self, name=None):
        '''A stock exchange record in an OrderedDict.
        '''
        name = (name or self.random_element(self.exchange_names))
        exid = self.exchange_ids[name]
        values = [
            exid, name, 0,
            self.generator.past_datetime().isoformat(),
            self.generator.past_datetime().isoformat(),
            self.generator.catch_phrase(),
            self.generator.address(),
        ]
        return OrderedDict(zip(self._exchange_keys, values))

    def issue(self):
        '''An security issue type.
        '''
        return self.random_element(self.issue_names)

    def dividend(self):
        '''A positive floating point number ##.##
        '''
        return self.generator.pyfloat(right_digits=2,
                                      left_digits=2,
                                      positive=True)


    def security(self, company):
        '''A company security record in an OrderedDict.

        company: A Company OrderedDict.
        '''
        values = [
            company['CO_SYMBOL'],
            self.issue(),
            self.identifier(prefix='ST'),
            company['CO_NAME'],
            company['CO_EX_ID'],
            self.identifier(prefix='CO'),
            0,
            self.generator.past_date().isoformat(),
            self.generator.past_date().isoformat(),
            self.cash(),
            self.cash(),
            self.generator.past_datetime().isoformat(),
            self.cash(),
            self.generator.past_datetime().isoformat(),
            self.dividend(),
            self.cash(),
        ]
        return OrderedDict(zip(self._security_keys, values))
    
    def holdings(self, account, securities, min=1, max=20):
        '''A list of Holding OrderedDicts.
        '''
        n_holdings = self.random_int(min=min,
                                     max=max)
        symbols = [s['S_SYMBOL'] for s in securities]
        self.generator.random.shuffle(symbols)
        return [self.holding(account, symbol)
                for symbol in symbols[:n_holdings]]

    def holding(self, account, symbol):
        '''An account holding record in an OrderedDict.

        account:    customer_account OrderedDict

        '''
        values = [
            self.identifier(prefix='T'),
            account['CA_ID'],
            symbol,
            self.generator.past_datetime().isoformat(),
            self.cash(),
            self.random_int(min=1),
        ]
        return OrderedDict(zip(self._holding_keys, values))

    def volume(self):
        '''
        '''
        return self.generator.randomint(min=1)

    def last_trade(self, securities):
        '''A last trade record in an OrderedDict
        '''
        security = self.random_element(securities)

        values = [
            security['S_SYMBOL'],
            self.generator.past_datetime().isoformat(),
            self.cash(),
            self.cash(),
            self.volume(),
        ]        
        return OrderedDict(zip(self._last_trade_keys, values))

    @functools.lru_cache(maxsize=None)
    def Company(self, company_id=None, index=None):
        '''A company record in a OrderedDict.
        '''

        if index is None:
            company_id = (company_id or
                          self.random_element(self.company_ids))
            n = self.company_ids.index(company_id)
        else:
            n = index
            company_id = self.company_ids[n]

        self._seed_instance(n)

        exchange = self.random_element(self.exchanges)

        values = [
            company_id,
            self.generator.company(),
            self.symbol(),
            exchange['EX_ID'],
            exchange['EX_NAME'],
        ]
        return OrderedDict(zip(self._company_keys, values))
