from open_publishing.core import DatabaseObjectsList

from .document_author import DocumentAuthor

class AuthorsList(DatabaseObjectsList):
    _database_object_type = DocumentAuthor

    def __init__(self,
                 document):
        super(AuthorsList, self).__init__(database_object=document,
                                          aspect='authors',
                                          list_locator = 'authors')
        self._document = document

    def add(self,
            first_name,
            last_name,
            user_id=None):
        res = self._database_object._context.gjp.create(DocumentAuthor._object_class,
                                                        first_name=first_name,
                                                        last_name=last_name,
                                                        document_id=self._document.document_id)


        author_id = DocumentAuthor.id_from_guid(res["GUID"])
        self._objects[author_id] = DocumentAuthor(context = self._document._context,
                                                  document_author_id = author_id)

        if(user_id):
            self._objects[author_id].user_id = user_id

        self._ids.append(author_id)

