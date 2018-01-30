from .core import Field
from .core import FieldDescriptor
from .core import FieldGroup
from .core import SimpleField

from .core.enums import ValueStatus, FieldKind, IsbnType

class IsbnField(Field):
    def __init__(self,
                 document,
                 name):
        super(IsbnField, self).__init__(document,
                                        'identifiers.*',
                                        FieldKind.readonly)
        self._name = name
        self._value = None

    @property
    def value(self):
        if self._status is ValueStatus.none:
            raise RuntimeError('Accessing to field which is not set')
        else :
            return self._value

    def hard_set(self,
                 value):
        pass

    def update(self,
               gjp):
        value = self._master_object(gjp)
        for fname in ['identifiers', 'isbns']:
            if fname in value:
                value = value[fname]
            else :
                value = None
                break
        if value is not None:
            if self._name in value:
                self._value = str(value[self._name]['ean'])
            else:
                self._value = None
            self._status = ValueStatus.soft

    def gjp(self,
            gjp):
        pass    


class RelatedIsbnsField(SimpleField):
    def __init__(self,
                 document):
        super(RelatedIsbnsField, self).__init__(document,
                                                'related_products_isbn',
                                                'related_products_isbn')
    
    def _parse_value(self,
                     value):
        if not value:
            return set()
        else:
            return set(value.split(';'))
                           
    def _value_validation(self,
                          value):
        if not isinstance(value, set):
            raise TypeError('Expected set, got : {0}'.format(type(value)))
        for i in value:
            if not isinstance(i, str):
                raise ValueError('Expected ISBN, got : {0}'.format(i))
        return value
                
    def _serialize_value(self,
                         value):
        return ';'.join({v.replace('-','')for v in value})
        
                 

class IsbnGroup(FieldGroup):
    def __init__(self,
                 document):
        super(IsbnGroup, self).__init__(document)
        self._document = document
        self._fields['pdf'] = IsbnField(document,
                                        'pdf')
        self._fields['epub'] = IsbnField(document,
                                         'epub')
        self._fields['mobi'] = IsbnField(document,
                                         'mobi')
        self._fields['pod'] = IsbnField(document,
                                        'pod')
        self._fields['related'] = RelatedIsbnsField(document)

    pdf = FieldDescriptor('pdf')
    epub = FieldDescriptor('epub')
    mobi = FieldDescriptor('mobi')
    pod = FieldDescriptor('pod')
    related = FieldDescriptor('related')

    def assign(self,
               isbn_type,
               isbn = None):
        if isbn_type not in IsbnType:
            raise ValueError('isbn_type should be one of op.isbn, got: {0}'.format(isbn_type))
        self._document.context.gjp.assign_isbn(self._document.document_id,
                                               isbn_type.identifier,
                                               isbn)
        self._document._fetch([])
        
