from open_publishing.imprint import Imprint

class Imprints(object):
    def __init__(self,
                 ctx):
        self._ctx = ctx
        self._imprints_lazy = None
        
        
    def _load(self,
             guid = None,
             imprint_id = None,
             fetch = True):
        if guid is None and imprint_id is None:
            raise TypeError('Neither guid nor imprint_id specified')
        elif guid is not  None and imprint_id is not None:
            raise TypeError('guid or imprint_id should be specified, nor both')
        elif guid is not None:
            imprint_id = Imprint.id_from_guid(guid)
        
        doc = Imprint(self._ctx,
                       imprint_id)
        if fetch:
            doc._fetch(["*"])
        return doc

    @property
    def _imprints(self):
        if self._imprints_lazy is None:
            _imprints_list = self._ctx.gjp.list_imprints()
            self._imprints_lazy = [self._load(imprint_id = int(key)) for key, value in list(_imprints_list.items())]
        return self._imprints_lazy
    

    def __iter__(self):
        return iter(self._imprints[:])

    def __getitem__(self, key):
        return self._imprints[key]

    def __len__(self):
        return len(self._imprints)

    def flush(self):
        if self._imprints is not None:
            for imprint in self._imprints:
                imprint.flush()

    def __repr__(self):
        return repr(list(iter(self)))

    def __str__(self):
        return str(list(iter(self)))



