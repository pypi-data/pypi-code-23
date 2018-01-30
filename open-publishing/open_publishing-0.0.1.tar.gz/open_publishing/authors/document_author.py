from open_publishing.core import SimpleField
from open_publishing.core import FieldDescriptor
from open_publishing.core import DatabaseObject
from open_publishing.core.enums import ContributorRole
from open_publishing.extendable_enum_field import ExtendableEnumField

class DocumentAuthor(DatabaseObject):
    _object_class = 'document_author'
    
    def __init__(self,
                 context,
                 document_author_id):
        super(DocumentAuthor, self).__init__(context,
                                             document_author_id)

        self._fields['first_name'] = SimpleField(database_object=self,
                                                 aspect=':basic',
                                                 field_locator='first_name',
                                                 dtype=str)

        self._fields['last_name'] = SimpleField(database_object=self,
                                                aspect=':basic',
                                                field_locator='last_name',
                                                dtype=str)

        self._fields['user_id'] = SimpleField(database_object=self,
                                                aspect=':basic',
                                                field_locator='user_id',
                                                dtype=int,
                                                nullable=True)

        self._fields['role'] = ExtendableEnumField(database_object=self,
                                                   aspect=':basic',
                                                   field_locator='contributor_role_id',
                                                   dtype=ContributorRole,
                                                   nullable=True,
                                                   serialized_null=0)
                                                       


    first_name = FieldDescriptor('first_name')
    last_name = FieldDescriptor('last_name')
    user_id = FieldDescriptor('user_id')
    role = FieldDescriptor('role')

    @property
    def document_author_id(self):
        return self._object_id

