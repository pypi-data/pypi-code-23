from open_publishing.core.enums import ValueStatus, FieldKind
from open_publishing.core import SequenceItem, SequenceField
from open_publishing.core import DatabaseObject, SimpleField, FieldDescriptor

class Genre(DatabaseObject):
    _object_class = 'realm_genre'

    def __init__(self,
                 context,
                 genre_id):
        super(Genre, self).__init__(context,
                                    genre_id)

        self._fields['name'] = SimpleField(database_object=self,
                                           aspect=':basic',
                                           field_locator='name',
                                           dtype=str,
                                           kind=FieldKind.readonly)
    name = FieldDescriptor('name')

    @property
    def genre_id(self):
        return self._object_id

    def __repr__(self):
        return '<Genre {0}>'.format(self.name)

    def __str__(self):
        return '{0}'.format(self.name)
    

class GenreItem(SequenceItem):
    def __init__(self,
                 genre):
        super(GenreItem, self).__init__(ValueStatus.soft)
        self._genre = genre

    @property
    def value(self):
        return self._genre

    @classmethod
    def from_gjp(cls, gjp, database_object):
        guid = gjp
        genre_id = Genre.id_from_guid(guid)
        genre = Genre(database_object.context,
                      genre_id)
        return cls(genre)

    def to_gjp(self):
        return self._genre.guid

class GenresList(SequenceField):
    _item_type = GenreItem
    
    def __init__(self,
                 document):
        super(GenresList, self).__init__(document,
                                        "non_academic.*",
                                        "non_academic.realm_genres")

    def add(self,
            genre):
        genre_obj = None
        if isinstance(genre, str):
            for obj in self.database_object.context.genres:
                if genre == obj.name:
                    genre_obj = obj
                    break
            else:
                raise ValueError('Genre name "{}" not found in ctx.genres'.format(genre))

        elif isinstance(genre, Genre):
            if genre in self.database_object.context.genres:
                genre_obj = genre
            else:
                raise ValueError('Genre "{}" not found in ctx.genres'.format(genre.guid))
        else:
            raise TypeError('Expected str or Genre, got: {0}'.format(type(genre)))

        if genre_obj.guid not in [i._genre.guid for i in self._list]:
            self._list.append(GenreItem(genre_obj))
        self._status = ValueStatus.hard
               
