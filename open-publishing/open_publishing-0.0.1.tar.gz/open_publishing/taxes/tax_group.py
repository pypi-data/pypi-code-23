from open_publishing.core import SimpleField, FieldDescriptor, FieldGroup

from .tax_field import TaxField

class TaxGroup(FieldGroup):
    def __init__(self,
                 user):
        super(TaxGroup, self).__init__(user)

        self._fields['vat_id'] = SimpleField(database_object=user,
                                             aspect='masterdata.*',
                                             field_locator='masterdata.vat_id',
                                             dtype=str)

        self._fields['tax_id'] = SimpleField(database_object=user,
                                                aspect='masterdata.*',
                                                field_locator='masterdata.tax_id',
                                                dtype=str)

        
        self._fields['authority'] = SimpleField(database_object=user,
                                                aspect='masterdata.*',
                                                field_locator='masterdata.tax_authority',
                                                dtype=str)

        self._fields['tax'] = TaxField(user)
                                      
    authority = FieldDescriptor('authority')
    vat_id = FieldDescriptor('vat_id')
    tax_id = FieldDescriptor('tax_id')
    tax = FieldDescriptor('tax')
