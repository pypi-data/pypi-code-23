from os import path
from xldeploy.http.http_client import get_content_type


class DeployfileService:
    __path = "/deployfile"

    def __init__(self, http_client):
        self.http_client = http_client
        self.headers = {'Content-Type': 'text/plain', 'Accept': 'text/plain'}

    def get_path(self, *args):
        return "/".join([self.__path] + list(args))

    def generate(self, directories):
        params = {"folder": directories}
        return self.http_client.get(path=self.get_path("generate"),
                                    headers=self.headers,
                                    params=params)

    def apply(self, deployfile, files):
        multi_part_files = []
        for file in files:
            filename = path.basename(file)
            # print("Resolved", get_content_type(filename), "for filename", filename)
            multi_part_files.append(('artifacts', (filename, open(file, 'rb'), get_content_type(filename))))

        # add deployfile as well to the multi-part encoded files post request
        multi_part_files.append(('deployFile', (deployfile, open(deployfile, 'r'), 'text/plain; charset="UTF-8"')))

        # print("Posting multipart-Encoded Artifact Files", multi_part_files, "to path", self.get_path("apply"))
        post = self.http_client.multipart_post(path=self.get_path("apply"), multiple_files=multi_part_files)
        return post
