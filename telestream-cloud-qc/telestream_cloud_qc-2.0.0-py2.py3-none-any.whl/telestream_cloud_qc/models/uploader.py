import requests
import json
import os
import threading

from ..rest import ApiException
from .extra_file import ExtraFile
from .upload_file import UploadFile
from .video_upload_body import VideoUploadBody


class Uploader(object):

    def __init__(self, factory_id, api_client, file_path, profiles, extra_files={}, threads=8, **kwargs):
        self.factory_id = factory_id
        self.api_client = api_client
        self.file_path = file_path
        self.profiles = profiles
        self.status = "created"
        self.files = []
        self.video_id = None
        self.error_message = None
        self.threads = threads
        self.tag_path_map = {}
        self.extra_files = self.__parse_extra_files(extra_files)
        self.location = None


    def setup(self):
        if self.status == 'created':
            try:
                video_upload_body = self.__initialize_video_upload_body()
                upload_session = self.api_client.upload_video(
                    self.factory_id, video_upload_body
                )
                self.location = upload_session.location
                self.__prepare_files(upload_session)
                self.status = 'initialized'
            except ApiException as e:
                print("Exception when calling %s->upload_video: %s\n" % (type(self.api_client).__name__, e))
                self.status = 'error'
        else:
            raise TelestreamCloudException('Already initialized')


    def is_uploaded(self):
        return len(list(filter(lambda x: x.status != "uploaded", self.files))) == 0


    def start(self, pos=0):
        if self.status == "initialized":
            self.status = "uploading"

            for upload_file in self.files:
                if upload_file.status != 'uploaded':
                    upload_file.start(pos)

                if upload_file.video_id:
                    self.video_id = upload_file.video_id

            if self.is_uploaded():
                self.status = 'uploaded'

            return self.video_id

        elif self.status == 'created':
            raise KeyError("Not initialized")
        else:
            raise KeyError("Already started")


    def resume(self):
        if self.status != 'uploaded':
            self.start()
        else:
            raise TelestreamCloudException('Files already uploaded')


    def abort(self):
        if self.status != 'uploaded':
            self.status = 'aborted'

            for upload_file in self.files:
                upload_file.abort()

            self.error_message = None
            res = requests.delete(self.location)
        else:
            raise TelestreamCloudException('Files already uploaded')


    def __parse_extra_files(self, files):
        extra_files = []
        file_info = lambda tag, file_path: {
            "tag" : tag,
            "file_name" : os.path.basename(file_path),
            "file_size" : os.stat(file_path).st_size,
            }
        for tag, path in files.items():
            if isinstance(path, type([])):
                for i in range(0, len(path)):
                    indexed_tag = "{}.index-{}".format(tag, i)
                    extra_files.append(file_info(indexed_tag, path[i]))
                    self.tag_path_map[indexed_tag] = path[i]
            else:
                extra_files.append(file_info(tag, path))
                self.tag_path_map[tag] = path
        return extra_files


    def __prepare_files(self, upload_session):
        self.files.append(
            UploadFile(upload_session.location, upload_session.parts,
                       upload_session.part_size, self.file_path, "",
                       threads=self.threads
            )
        )
        if upload_session.extra_files:
            for key, extra_file in upload_session.extra_files.items():
                self.files.append(
                    UploadFile(
                        upload_session.location, int(extra_file["parts"]),
                        int(extra_file["part_size"]),
                        self.tag_path_map.get(extra_file["tag"]), extra_file["tag"],
                        threads=self.threads
                    )
                )

    def __initialize_video_upload_body(self):
        file_name = os.path.basename(self.file_path)
        file_size = os.stat(self.file_path).st_size
        return VideoUploadBody(
            file_name=file_name, file_size=file_size, profiles=self.profiles,
            extra_files=self.__initialize_extra_files()
        )

    def __initialize_extra_files(self):
        return [
            ExtraFile(
                file_name=ef_data['file_name'], file_size=ef_data['file_size'],
                tag=ef_data['tag']
            ) for ef_data in self.extra_files
        ]
