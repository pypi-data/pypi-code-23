from open_publishing.core import FieldGroup
from open_publishing.core import FieldDescriptor
from open_publishing.core.enums import TaxType
from open_publishing.core import SimpleField

class TaxTypeBase(FieldGroup):
    _catalog_type = None
    def __init__(self,
                 user):
        super(TaxTypeBase, self).__init__(user)
        self._fields['vat_percentage'] = SimpleField(database_object=user,
                                                     aspect='masterdata.*',
                                                     field_locator='masterdata.vat_percentage',
                                                     dtype=int)

        self._fields['eu_reverse_charge'] = SimpleField(database_object=user,
                                                            aspect='masterdata.*',
                                                            field_locator='masterdata.vat_eu_reverse_charge',
                                                            dtype=bool)
        
        
    _vat_percentage = FieldDescriptor('vat_percentage')
    _eu_reverse_charge = FieldDescriptor('eu_reverse_charge')

    @property
    def tax_type(self):
        return self._tax_type

class NoTax(TaxTypeBase):
    _tax_type = TaxType.no_tax
    def __init__(self,
                 user):
        super(NoTax, self).__init__(user)

class EUReverseCharge(TaxTypeBase):
    _tax_type = TaxType.eu_reverse_charge
    def __init__(self,
                 user):
        super(EUReverseCharge, self).__init__(user)

class VATPercentage(TaxTypeBase):
    _tax_type = TaxType.vat_percentage
    def __init__(self,
                 user):
        super(VATPercentage, self).__init__(user)

    @property
    def percentage(self):
        return self._vat_percentage

    @percentage.setter
    def percentage(self,
                   value):
        if value not in [7, 19]:
            raise ValueError('Percenrage should be 7 or 19 (for 0 use op.tax.NoTax), got: {0}'.format(value))
        self._vat_percentage = value
        
