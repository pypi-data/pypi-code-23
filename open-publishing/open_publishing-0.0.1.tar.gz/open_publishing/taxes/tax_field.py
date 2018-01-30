from open_publishing.core.enums import ValueStatus
from open_publishing.core import Field

from . import tax_types 

class TaxField(Field):
    def __init__(self,
                 user):
        super(TaxField, self).__init__(database_object=user,
                                       aspect="masterdata.*" )
        self._value = None

    @property
    def value(self):
        if self.status is ValueStatus.none:
            raise RuntimeError("Accessing to field which is not set")
        else :
            return self._value

    def hard_set(self,
                 value):
        if isinstance(value, tax_types.VATPercentage):
            self._value = tax_types.VATPercentage(self._database_object) 
        elif isinstance(value, tax_types.EUReverseCharge):
            self._value = tax_types.EUReverseCharge(self._database_object) 
        elif isinstance(value, tax_types.NoTax):
            self._value = tax_types.NoTax(self._database_object)
        else :
            raise ValueError("Expected instance of Academic or NonAcademic, got {0}".format(type(value)))
        self._value.hard_set(value)
        self._status = ValueStatus.hard

    def update(self,
               gjp):
        if self._status is not ValueStatus.hard:
            master_obj = self._master_object(gjp)
            if 'masterdata' in master_obj:
                masterdata=master_obj['masterdata']
                if ('vat_eu_reverse_charge' in masterdata and
                    'vat_percentage' in masterdata):

                    tax_id = masterdata['tax_id']
                    vat_id = masterdata['vat_id']
                    vat_percentage = masterdata['vat_percentage']
                    vat_eu_reverse_charge = masterdata['vat_eu_reverse_charge']

                    if vat_eu_reverse_charge == True and vat_percentage == 0:
                        self._value = tax_types.EUReverseCharge(self._database_object)
                    elif vat_percentage != 0:
                        self._value = tax_types.VATPercentage(self._database_object)
                    elif vat_percentage == 0 and vat_eu_reverse_charge == False:
                        self._value = tax_types.NoTax(self._database_object)
                    else:
                        raise RuntimeError('Inconsistency in taxes vat_percentage: {0}, vat_eu_reverse_charge: {1}'.format(tax_id,
                                                                                                                           vat_id,
                                                                                                                           vat_percentage,
                                                                                                                           vat_eu_reverse_charge))
                    self._status = ValueStatus.soft
        if self._status is not ValueStatus.none:
            self._value.update(gjp)
            
    def gjp(self,
            gjp):
        if self._status is not ValueStatus.none:
            self._value.gjp(gjp)
