
class MetadataService:

    __path = "/metadata"

    def __init__(self, http_client):
        self.http_client = http_client

    def get_path(self, *args):
        return "/".join([self.__path] + list(args))

    def list_descriptors(self):
        return self.http_client.get(path=self.get_path("type"))
