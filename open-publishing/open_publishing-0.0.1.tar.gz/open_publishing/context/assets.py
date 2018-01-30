from open_publishing.assets import AssetLink

class Assets(object):
    def __init__(self,
                 context):
        self._ctx = context

    def link(self, file_id):
        return AssetLink(self._ctx, file_id)

