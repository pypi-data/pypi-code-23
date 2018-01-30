from copy import deepcopy
import datetime
import os

from open_publishing.core import SimpleField
from open_publishing.core.enums import FieldKind

class ArchiveField(SimpleField):
    def __init__(self,
                 document):
        super(ArchiveField, self).__init__(database_object=document,
                                           aspect='directory',
                                           field_locator='directory',
                                           kind=FieldKind.readonly)
    
    def _parse_value(self,
                     value):
        if value is None:
            return ArchiveRootDirectory(self.database_object, {'name': '',
                                                               'children': {}})
        else:
            return ArchiveRootDirectory(self.database_object, value['directory'])
        
    def _value_validation(self,
                          value):
        pass
    
    def _serialize_value(self,
                         value):
        pass

        

class ArchiveItem(object):
    def __init__(self,
                 document,
                 desc):
        self._name = desc['name']
        self._document = document

    @property
    def name(self):
        return self._name


class ArchiveDirectory(ArchiveItem):
    def __init__(self,
                 document,
                 directory_desc):
        super(ArchiveDirectory, self).__init__(document,
                                               directory_desc)
        self._name = directory_desc['name']
        self._children = {}
        for child in directory_desc['children']:
            if len(child) != 1:
                raise ValueError('unexpected data structure, "{0}"'.format(child))
            item_type, item_desc = list(child.items())[0]

            if item_type == 'directory' and 'grin_url' in item_desc:
                self._children[item_desc['name']] = ArchiveCompressedDirectory(self._document,
                                                                               item_desc)
            elif item_type == 'directory' and 'grin_url' not in item_desc:
                self._children[item_desc['name']] = ArchiveDirectory(self._document,
                                                                     item_desc)
            elif item_type == 'file':
                self._children[item_desc['name']] = ArchiveFile(self._document,
                                                                item_desc)
            else:
                raise ValueError('Unexpected item_type: "{0}"'.format(item_type))

    def __iter__(self):
        return iter(list(self._children.items()))

    def __getitem__(self, key):
        return self._children[key]

    def __len__(self):
        return len(self._children)

    def _walk(self, dir, prefix, walk_in_compressed):
        for name, item in list(dir._children.items()):
            if prefix:
                path = os.path.join(prefix, name)
            else :
                path = name
            if isinstance(item, ArchiveCompressedDirectory):
                yield path , item
                if walk_in_compressed:
                    for res in self._walk(item, path, walk_in_compressed):
                        yield res
            elif isinstance(item, ArchiveDirectory):
                for res in self._walk(item, path, walk_in_compressed):
                    yield res

            elif isinstance(item, ArchiveFile):
                yield path, item

    def walk(self, walk_in_compressed = False):
        for res in self._walk(self, "", walk_in_compressed):
            yield res
        
class ArchiveFile(ArchiveItem):
    def __init__(self,
                 document,
                 file_desc):
        super(ArchiveFile, self).__init__(document,
                                          file_desc)
        self._name = file_desc['name']
        self._size = int(file_desc['size'])
        self._url = file_desc['grin_url']
        
    @property
    def size(self):
        return self._size

    @property
    def url(self):
        return self.url

    def download(self):
        return self._document.context.gjp.download_from_archive(self._url)
    
    def save(self,
             file_name):
        with open(file_name, 'wb') as f:
            f.write(self.download())


class ArchiveCompressedDirectory(ArchiveDirectory, ArchiveFile):
    def __init__(self,
                 document,
                 file_desc):
        super(ArchiveCompressedDirectory, self).__init__(document,
                                                         file_desc)

class ArchiveRootDirectory(ArchiveDirectory):
    def __init__(self,
                 document,
                 file_desc):
        super(ArchiveRootDirectory, self).__init__(document,
                                                   file_desc)

    def _split_path(self, path):
        path = os.path.normpath(path)
        if path[0] in ['/', '.']:
            raise ValueError('invalid path "{0}"'.format(path))

        path_list = []
        while path != '':
            path_list = [os.path.basename(path)] + path_list
            path = os.path.dirname(path)
        return path_list
        
    def find(self, path):
        item = self
        for name in self._split_path(path):
            item = item._children[name]
        return item
        
    def download(self, path):
        return self.find(path).download()
        
    def save(self,
             path,
             file_name):
        with open(file_name, 'wb') as f:
            f.write(self.download(path))

    def isdir(self, path):
        if isinstance(self.find(path), ArchiveDirectory):
            return True
        return False
        
    def isfile(self, path):
        if isinstance(self.find(path), ArchiveFile):
            return True
        return False

    def exists(self, path):
        item = self
        for name in self._split_path(path):
            if name in item._children:
                item = item._children[name]
            else:
                return False
        return True


