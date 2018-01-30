from open_publishing.genre import Genre

class Genres(object):
    def __init__(self,
                 ctx):
        self._ctx = ctx
        self._genres_lazy = None

    def create(self,
               name):
        res = self._ctx.gjp.create(Genre._object_class,
                                   name=name)

        
        genre_id = Genre.id_from_guid(res["GUID"])
        genre = Genre(self._ctx,
                       genre_id)
        genre._fetch([":basic"])
        self._genres_lazy = None
        return genre

        
    def _load(self,
             guid = None,
             genre_id = None,
             fetch = True):
        if guid is None and genre_id is None:
            raise TypeError('Neither guid nor genre_id specified')
        elif guid is not  None and genre_id is not None:
            raise TypeError('guid or genre_id should be specified, nor both')
        elif guid is not None:
            genre_id = Genre.id_from_guid(guid)
        
        doc = Genre(self._ctx,
                    genre_id)
        if fetch:
            doc._fetch([":basic"])
        return doc

    @property
    def _genres(self):
        if self._genres_lazy is None:
            _genres_list = self._ctx.gjp.list_genres()
            self._genres_lazy = [self._load(genre_id = int(key)) for key, value in list(_genres_list.items())]
        return self._genres_lazy
    

    def __iter__(self):
        return iter(self._genres[:])

    def __getitem__(self, key):
        return self._genres[key]

    def __len__(self):
        return len(self._genres)

    def flush(self):
        if self._genres is not None:
            for genre in self._genres:
                genre.flush()

    def __repr__(self):
        return repr(list(iter(self)))

    def __str__(self):
        return str(list(iter(self)))



