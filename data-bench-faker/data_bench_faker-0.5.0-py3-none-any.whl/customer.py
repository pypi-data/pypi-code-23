
from .base import DataBenchProvider

from collections import OrderedDict
import functools

class CustomerProvider(DataBenchProvider):

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

    _customer_keys = [
        'C_ID',
        'C_TAX_ID', 'C_ST_ID',
        'C_L_NAME', 'C_F_NAME', 'C_M_NAME',
        'C_GENDER',
        'C_TIER',
        'C_DOB',
        'C_AD_ID',
        'C_COUNTRY_1', 'C_AREA_1', 'C_LOCAL_1', 'C_EXT_1',
        'C_COUNTRY_2', 'C_AREA_2', 'C_LOCAL_2', 'C_EXT_2',
        'C_COUNTRY_3', 'C_AREA_3', 'C_LOCAL_3', 'C_EXT_3',
        'C_EMAIL_1',
        'C_EMAIL_2',
        'C_NACCTS',
    ]

    _customer_account_keys = [
        'CA_C_ID',
        'CA_ID',
        'CA_TAX_ID',
        'CA_B_ID',
        'CA_NAME',
        'CA_BAL',
        'CA_L_NAME',
        'CA_F_NAME',
        'CA_M_NAME',
    ]

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
    def scaled(cls, nb_customers=150000, base_seed=0, base_id=4300000000):
        '''
        '''
        attrs = {
            'nb_customers':nb_customers,
            'base_seed':base_seed,
            'base_id':base_id,
        }

        scale = int(nb_customers/1000)
        
        return type('ScaledCustomerProvider',
                    (CustomerProvider,),
                    attrs)

    @functools.lru_cache(maxsize=None)
    def customers(self):
        '''
        '''
        base = self.base_id + 1
        id_range = range(base, base+self.nb_cusotmers)
        return [self.customer(c_id) for c_id in id_range]

    def trading_tier(self):
        '''A customer's trading tier.
        '''
        return self.random_element(self.trading_tiers)

    def date_of_birth(self, low=18, hi=110):
        '''Date Of Birth
        '''
        yy = self.generator.random_int(min=1901, max=2018)
        mm = self.generator.random_int(min=1, max=12)
        dd = self.generator.random_int(min=1, max=31)

        return f'{yy}-{mm:02d}-{dd:02d}'


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
    def customer(self, index=None):
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
            index = self.generator.random_int(min=0, max=self.nb_customers)

        customer_id = self.base_id + index + 1
            
        self.set_seed(index)
        
        gender, f_name, m_initial, l_name = self.gendered_name_tuple()

        tier = self.trading_tier()
        r = self.accounts_per_tier[tier]
        naccounts = self.generator.random_int(min=r.start,
                                              max=r.stop)
        values = [
            customer_id,
            self.tax_id(),
            self.identifier(prefix='ST-'),
            l_name, f_name, m_initial,
            gender,
            tier,
            self.date_of_birth(),
            self.generator.address(),
            self.numerify('+!'), self.numerify('###'),
            self.numerify('###-####'), self.numerify('####'),
            self.numerify('+!'), self.numerify('###'),
            self.numerify('###-####'), self.numerify('####'),
            self.numerify('+!'), self.numerify('###'),
            self.numerify('###-####'), self.numerify('####'),
            self.generator.email(),
            self.generator.email(),
            naccounts,
        ]
        return OrderedDict(zip(self._customer_keys, values))

    @functools.lru_cache(maxsize=None)
    def accounts(self):
        '''A list of customer account records.
        '''
        l = []
        for n, customer in enumerate(self.customers()):
            self.set_seed(n)
            for _ in range(customer['C_NACCTS']):
                l.append(self.account(customer))
        return l

    def account_name(self, customer=None):
        '''A customer account name string.
        '''
        customer = (customer or self.customer())
        label = self.generator.random_element(self.account_name_labels)
        return ' '.join([customer['C_F_NAME'],
                         customer['C_L_NAME'],
                         label])

    def account(self, customer=None):
        '''A customer acount record.
        '''
        
        customer = (customer or
                    self.generator.random_element(self.customers()))

        values = [
            customer['C_ID'],
            self.identifier(prefix='CA-'),
            customer['C_TAX_ID'],
            self.identifier(prefix='B-'),
            self.account_name(customer=customer),
            self.cash(),
            customer['C_L_NAME'],
            customer['C_F_NAME'],
            customer['C_M_NAME'],
        ]
        return OrderedDict(zip(self._customer_account_keys, values))

        
