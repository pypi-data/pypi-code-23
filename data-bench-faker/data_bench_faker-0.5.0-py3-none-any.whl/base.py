
from faker.providers import BaseProvider


class DataBenchProvider(BaseProvider):
    '''
    '''
    base_seed = 0
    n_customers = 1000
    
    tax_id_formats = {
        '##-#######':  0.5,
        '###-##-####': 0.5
    }

    def set_seed(self, seed):
        '''
        '''
        self.generator.seed(seed + self.base_seed)

    def identifier(self, prefix=None, count=10, suffix=None):
        '''A string numeric identifier with optional string prefix.
        '''
        digit = '#'
        prefix = (prefix or '')
        suffix = (suffix or '')
        return self.numerify(f'{prefix}{digit * count}{suffix}')

    def tax_id(self):
        '''A US tax identfier in either EIN or SSN format.

        Associated with a customer.
        '''
        tax_id_fmt = self.random_element(self.tax_id_formats)
        return self.numerify(tax_id_fmt)

    def cash(self):
        '''
        '''
        return self.generator.pyfloat(left_digits=5,
                                      right_digits=2,
                                      positive=True)
