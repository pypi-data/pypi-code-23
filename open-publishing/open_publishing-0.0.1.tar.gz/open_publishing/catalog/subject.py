from open_publishing.core.enums import ValueStatus, FieldKind
from open_publishing.core import Field, DatabaseObject, SimpleField, FieldDescriptor
from .bisac import BisacSubject

class Subject(DatabaseObject):
    _object_class = 'subject'

    def __init__(self,
                 context,
                 subject_id):
        super(Subject, self).__init__(context,
                                      subject_id)

        self._fields['bisac'] = BisacSubjectField(subject=self)

    bisac = FieldDescriptor('bisac')

    @property
    def subject_id(self):
        return self._object_id

    def __repr__(self):
        return '<Subject {0}>'.format(self.name)

    def __str__(self):
        return '{0}'.format(self.name)
    
class SubjectField(SimpleField):
    def __init__(self,
                 document):
        super(SubjectField, self).__init__(database_object=document,
                                           aspect='academic.*',
                                           field_locator='academic.subject')

    def _parse_value(self,
                     value):
        if value:
            return Subject(self.database_object.context,
                           subject_id=Subject.id_from_guid(value))
        else:
            return None

    def _value_validation(self,
                          value):
        if value is None:
            return None
        elif isinstance(value, Subject):
            return value
        elif isinstance(value, int):
            return Subject(self.database_object.context,
                           subject_id=value)
        elif isinstance(value, str):
            return Subject(self.database_object.context,
                           subject_id=Subject.id_from_guid(value))
        else:
            raise TypeError("expected instance of subject, subject_id, subject_guid or None, got instance of {0}".format(type(value)))

    def _serialize_value(self,
                         value):
        if value is None:
            return None
        else:
            return value.guid

class BisacSubjectField(SimpleField):
    def __init__(self,
                 subject):
        super(BisacSubjectField, self).__init__(database_object=subject,
                                                aspect=':basic',
                                                field_locator='bisac_subject_id',
                                                kind=FieldKind.readonly)
        self._bisac_subject_id = None
        self._bisac_subject = None

    def flush(self):
        if self._bisac_subject:
            self._bisac_subject.flush()
    
    def _parse_value(self,
                     value):
        self._bisac_subject_id = value
        self._bisac_subject = BisacSubject(self.database_object.context, self._bisac_subject_id)
        return self._bisac_subject
        
    def _value_validation(self,
                          value):
        pass
    
    def _serialize_value(self,
                         value):
        pass


    
