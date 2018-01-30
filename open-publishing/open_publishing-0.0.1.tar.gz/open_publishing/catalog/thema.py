from datetime import datetime

from open_publishing.core import SequenceItem, SequenceField
from open_publishing.core import DatabaseObject, FieldDescriptor, SimpleField
from open_publishing.core.enums import ValueStatus, FieldKind, ThemaCode

class ThemaSubject(DatabaseObject):
    _object_class = 'thema_subject'
    
    def __init__(self,
                 context,
                 thema_subject_id):
        super(ThemaSubject, self).__init__(context,
                                           thema_subject_id)

        self._fields['code'] = SimpleField(database_object=self,
                                           aspect='*',
                                           field_locator='code',
                                           dtype=ThemaCode,
                                           kind=FieldKind.readonly)

        self._fields['name'] = SimpleField(database_object=self,
                                           aspect='*',
                                           field_locator='screenname',
                                           dtype=str,
                                           kind=FieldKind.readonly)



    code = FieldDescriptor('code')
    name = FieldDescriptor('name')


class Thema(SequenceItem):
    def __init__(self,
                 subject):
        super(Thema, self).__init__(ValueStatus.soft)
        self._subject = subject

    @property
    def value(self):
        return self._subject
    
    @classmethod
    def from_gjp(cls, gjp, database_object):
        guid = gjp
        subject_id = ThemaSubject.id_from_guid(guid)
        subject = ThemaSubject(database_object.context,
                               subject_id)
        return cls(subject)

    def to_gjp(self):
        return self._subject.guid

class ThemaList(SequenceField):
    _item_type = Thema
    
    def __init__(self,
                 document):
        super(ThemaList, self).__init__(document,
                                        "thema_subjects",
                                        "thema_subjects")

    def add(self,
            thema_code):
        if thema_code in ThemaCode:
            subject_id = self.database_object.context.gjp.resolve_enum(ThemaCode,
                                                                       enum=thema_code).internal_id
        else:
            subject_id = self.database_object.context.gjp.resolve_enum(ThemaCode,
                                                                       code=thema_code).internal_id
        subject = ThemaSubject(self.database_object.context,
                               subject_id)
        
        new_thema = Thema(subject)
        self._list.append(new_thema)
        self._status = ValueStatus.hard
               

