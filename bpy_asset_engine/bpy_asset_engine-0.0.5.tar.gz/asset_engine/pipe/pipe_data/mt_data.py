class MakeTheoryTask(object):
    def __init__(self, **kwargs):
        # for key, value in kwargs.items():
        #     setattr(self, key, value)
        self.artist_name = kwargs.setdefault('artist_name', None)
        self.asset_category_id = kwargs.setdefault('asset_category_id', None)
        self.asset_folder = kwargs.setdefault('asset_folder', None)
        self.asset_id = kwargs.setdefault('asset_id', None)
        self.asset_name = kwargs.setdefault('asset_name', None)
        self.asset_parent_id = kwargs.setdefault('asset_parent_id', None)
        self.state_name = kwargs.setdefault('state_name', None)
        self.task_artist_id = kwargs.setdefault('task_artist_id', None)
        self.task_creation_date = kwargs.setdefault('task_creation_date', None)
        self.task_name = kwargs.setdefault('task_name', None)
        self.task_task_id = kwargs.setdefault('task_task_id', None)
        self.version = kwargs.setdefault('version', None)
        self.version_creationDate = kwargs.setdefault('version_creationDate', None)
        self.version_id = kwargs.setdefault('version_id', None)


class MakeTheoryAsset(object):
    def __init__(self, **kwargs):
        # for key, value in kwargs.items():
        #     setattr(self, key, value)
        self.asset_category_id = kwargs.setdefault('asset_category_id', None)
        self.asset_creationDate = kwargs.setdefault('asset_creationDate', None)
        self.asset_parent_id = kwargs.setdefault('asset_parent_id', None)
        self.id = kwargs.setdefault('id', None)
        self.name = kwargs.setdefault('name', None)
        self.parent_id = kwargs.setdefault('parent_id', None)


class MakeTheoryShot(object):
    def __init__(self, **kwargs):
        # for key, value in kwargs.items():
        #     setattr(self, key, value)
        self.asset_category_id = kwargs.setdefault('asset_category_id', None)
        self.asset_creationDate = kwargs.setdefault('asset_creationDate', None)
        self.asset_folder = kwargs.setdefault('asset_folder', None)
        self.asset_parent_id = kwargs.setdefault('asset_parent_id', None)
        self.id = kwargs.setdefault('id', None)
        self.name = kwargs.setdefault('name', None)
        self.parent_id = kwargs.setdefault('parent_id', None)


class MakeTheoryFolder(object):
    def __init__(self, **kwargs):
        self.id = kwargs.setdefault('id', None)
        self.is_file = kwargs.setdefault('is_file', None)
        self.mimeType = kwargs.setdefault('mimeType', None)
        self.modifiedDate = kwargs.setdefault('modifiedDate', None)
        self.parent_id = kwargs.setdefault('parent_id', None)
        self.publisher = kwargs.setdefault('publisher', None)
        self.title = kwargs.setdefault('title', None)
        self.url = kwargs.setdefault('url', None)


class MakeTheoryFile(MakeTheoryFolder):
    def __init__(self, **kwargs):
        self.fileExtension = kwargs.setdefault('fileExtension', None)
        self.fileSize = kwargs.setdefault('fileSize', None)
        super(self.__class__, self).__init__(**kwargs)
        MakeTheoryFolder.__init__(self, **kwargs)



