import open_publishing.gjp

from .document import Document

class DocumentListItem(Document):

    def __init__(self,
                 context,
                 document_id,
                 document_list):
        super(DocumentListItem, self).__init__(context,
                                               document_id)
        self._document_list = document_list

    def _fetch(self,
               aspect):
        self._document_list._fetch(aspect)

    def _on_changed(self):
        self._context.documents._add_to_changed(self._document_list)

    def _on_flush(self):
        pass


class DocumentList(object):
    def __init__(self,
                 context,
                 documents_ids):
        self._context = context
        self._documents = [DocumentListItem(self._context,
                                            document_id,
                                            self) for document_id in documents_ids]


    def _fetch(self,
               aspect):
        gjp = self._context.gjp.get_chunk(guids=[doc.guid for doc in self._documents],
                                              fields=aspect)
        for doc in self._documents:
            doc._update(gjp)

    def flush(self):
        gjp_all = []
        for doc in self._documents:
            gjp = doc._gjp()
            if gjp:
                gjp_all.append({'guid' : doc.guid,
                                'version' : doc._version,
                                'gjp' : gjp})

        if gjp_all:
            for doc in self._documents:
                if doc._version is None:
                    self._fetch([])
                    break
            try:
                self._context.gjp.update_chunk(gjp_all)
            except open_publishing.gjp.ObjectHasChanged:
                self._fetch([])
                self._context.gjp.update_chunk(gjp_all)
        self._context.documents._remove_from_changed(self)

                
    def __enter__(self):
        return self

    def __exit__(self, exception_type, exception_value, traceback):
        self.flush()
        
        
    def __iter__(self):
        return iter(self._documents)

    def __len__(self):
        return len(self._documents)

    def __getitem__(self, key):
        return self._documents[key]
