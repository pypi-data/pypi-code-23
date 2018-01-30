import datetime

from .core.enums import AssetsModules, AssetsCoverType, ValueStatus
from .core import FieldGroup
from .core import SequenceItem, SequenceField
from .core import FieldDescriptor

from .gjp.stubbornness import RetryNotPossible
from .content import Content

class AssetNotReady(Exception):
    pass 

class AssetExpired(RetryNotPossible, Exception):
    pass 

    
class AssetLink(object):
    def __init__(self,
                 ctx,
                 file_id):
        self._ctx = ctx
        self._file_id = file_id

    @property
    def file_id(self):
        return self._file_id

    def download(self):
        status, data, headers = self._ctx.gjp.request_file(self._file_id)
        if status == 'ready':
            return Content(data, headers)
        elif status in ['new', 'inprogress']:
            raise AssetNotReady('Status: {0}'.format(status))
        elif status in ['expired']:
            raise AssetExpired('Status: {0}'.format(status))
        else:
            ValueError('Unexpected status: {0}'.format(status))

    def save(self,
             filename = None):
        content = self.download()
        with open(filename if filename else content.filename, 'wb') as f:
            f.write(content.data)

class OriginalAssetLink(object):
    def __init__(self,
                 ctx,
                 file_id):
        self._ctx = ctx
        self._file_id = file_id

    @property
    def file_id(self):
        return self._file_id

    def download(self):
        return self._ctx.gjp.download_asset(self._file_id)

    def save(self,
             file_name):
        with open(file_name, 'wb') as f:
            f.write(self.download())

            
class AssetsGroup(FieldGroup):
    def __init__(self,
                 document):
        super(AssetsGroup, self).__init__(document)
        self._document = document
        self._fields['original'] = OriginalAssetsList(document)

    original = FieldDescriptor('original')
        

    def _create_file(self, module, **params):
        file_id = self._document.context.gjp.create_file(self._document.document_id,
                                                         module,
                                                         **params)
        return AssetLink(self._document.context, file_id)

    def cover(self,
              cover_type):
        if cover_type not in AssetsCoverType:
            raise ValueError('Asset type should be on of op.assets.cover.*, got {0}'.format(cover_type))
        return self._create_file(AssetsModules.cover, type=cover_type)

    def epub(self,
             channel):
        if not isinstance(channel, str):
            raise ValueError('Channel should be string, got {0}'.format(channel))
        return self._create_file(AssetsModules.epub, channel=channel)

    def mobi(self):
        return self._create_file(AssetsModules.mobi)

    def pdf(self):
        return self._create_file(AssetsModules.pdf)

    def extract(self):
        return self._create_file(AssetsModules.extract)
    

class OriginalAsset(SequenceItem):
    def __init__(self,
                 ctx,
                 filename,
                 file_id,
                 timestamp):
        super(OriginalAsset, self).__init__(ValueStatus.soft)
        self._ctx = ctx
        self._filename = filename
        self._file_id = file_id
        self._timestamp = timestamp

    @property
    def filename(self):
        return self._filename

    @property
    def link(self):
        return OriginalAssetLink(self._ctx, self._file_id)

    @property
    def timestamp(self):
        return self._timestamp

    @classmethod
    def from_gjp(cls, gjp, database_object):
        filename = gjp['original_filename']
        file_id = gjp['id']
        timestamp = datetime.datetime.fromtimestamp(gjp['upload_timestamp'])
        return cls(database_object.context,
                   filename,
                   file_id,
                   timestamp)
    

class OriginalAssetsList(SequenceField):
    _item_type = OriginalAsset
    
    def __init__(self,
                 document):
        super(OriginalAssetsList, self).__init__(document,
                                                 'uploaded_files',
                                                 'uploaded_files')
