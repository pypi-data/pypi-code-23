from open_publishing.document import Document
from open_publishing.document_list import DocumentList
from open_publishing.catalog.public import NonAcademic
from open_publishing.prices.public import NoPrice

class Documents(object):
    def __init__(self,
                 ctx):
        self._ctx = ctx
        self._refs = set() #TODO: Consider using weakref

    def load_list(self,
                  guids = None,
                  documents_ids = None,
                  fetch = True):
        if guids is None and documents_ids is None:
            raise TypeError('Neither guid nor document_id specified')
        elif guids is not  None and documents_ids is not None:
            raise TypeError('guid or document_id should be specified, not both')
        elif guids is not None:
            documents_ids = [Document.id_from_guid(guid) for guid in guids]
        
        docs = DocumentList(self._ctx,
                            documents_ids)
        if fetch:
            docs._fetch([":basic"])
        return docs
        
    def load(self,
             guid = None,
             document_id = None,
             ean = None,
             isbn = None,
             fetch = True):
        if len([x for x in [guid, document_id, ean, isbn] if x is not None]) != 1:
            raise TypeError('Exectly one of guid/document_id/ean/isbn should be specified')
        if guid is not None:
            document_id = Document.id_from_guid(guid)
        elif ean is not None:
            document_id = self._ctx.gjp.resolve_ean(ean)['document_id']
        elif isbn is not None:
            document_id = self._ctx.gjp.resolve_ean(isbn.replace('-',''))['document_id']
            
        doc = Document(self._ctx,
                       document_id)
        if fetch:
            doc._fetch([":basic"])
        return doc
        
    def create(self,
               title):
        res = self._ctx.gjp.create(Document._object_class,
                                   title=title)
        
        document_id = Document.id_from_guid(res["GUID"])
        doc = Document(self._ctx,
                       document_id)
        doc._fetch([":basic"])
        with doc:
            doc.catalog = NonAcademic()
            doc.self_publishing = False
            doc.prices.pod = NoPrice()
            doc.prices.ebook = NoPrice()
        return doc


    def search(self,
               query = None,
               status = None,
               created = None,
               language = None,
               page_count = None,
               license = None):
        """
        Search for documents

        Params:
        query - string query

        These are additional filters:
        status - one of op.status.(new|published|unapproved|deleted)
                 any subset of it in iterable container.
        created - instance of datetime.date for precice date, or tuple of two dates
                 (from_date, to_date). `from_date` or `to_date` can be None, in meaning of open
                 period of time.
        language - one of op.language.*
        page_count - int, tuple of two elements or list of ints and of tuples. When int,
                 searching for precice page count. Tuple of two elements specifies range
                 of page counts. List of ints and tuples specifies desired page counts
                 and page ranges.
        license - one of op.license.*
        """
        res = self._ctx.gjp.documents_search(query=query,
                                             status=status,
                                             created=created,
                                             language=language,
                                             page_count=page_count,
                                             license=license)
        guids = [ obj["GUID"] for obj in res ]
        docs = [self.load(guid=guid, fetch=False) for guid in guids]
        return docs

    def flush(self):
        refs = self._refs.copy()
        for doc in refs:
            doc.flush()
        self._refs = set()

    def _add_to_changed(self,
                        database_object):
        self._refs.add(database_object)

    def _remove_from_changed(self,
                             database_object):
        if database_object in self._refs:
            self._refs.remove(database_object)
