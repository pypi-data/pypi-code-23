import threading
import os
import requests
import json

class UploadFile(object):
    def __init__(self, location, parts, part_size, file_name, tag, threads = 8):
        self.location = location
        self.file_name = file_name
        self.file_size = os.stat(file_name).st_size
        self.tag = tag

        self.part_size = part_size
        self.parts = parts
        self.missing_parts = [i for i in range(self.parts - 1, -1, -1)]

        self.status = "initialized"
        self.video_id = None
        self.error_message = None

        self.n_threads = threads
        self.lock = threading.Lock()


    def read_chunks(self):
        while True:
            self.lock.acquire()

            if not self.missing_parts:
                self.lock.release()
                break

            i = self.missing_parts.pop()

            self.file_object.seek(i * self.part_size)
            data = self.file_object.read(self.part_size)

            self.lock.release()

            if not data:
                break

            yield (data,i)


    def send_chunks(self):
        for chunk, i in self.read_chunks():
            if self.status == "aborted":
                break

            res = requests.post(self.location, headers={
                'Content-Type': 'application/octet-stream',
                'Cache-Control': 'no-cache',
                'X-Extra-File-Tag' : self.tag,
                'X-Part' : str(i),
                'Content-Length' : str(min(self.part_size, len(chunk))), },
                                data = chunk)

            if res.text and json.loads(res.text)["status"] in ("processing"):
                self.status = "uploaded"
                self.video_id = res.json().get('id')


    def start(self, pos=0):
        if self.status == "initialized":
            self.status = "uploading"

            self.file_object = open(self.file_name, "rb")

            if self.n_threads > 1:
                threads = []

                for i in range(0, self.n_threads):
                    thread = threading.Thread(target=self.send_chunks)
                    threads.append(thread)
                    thread.start()

                for thread in threads:
                    thread.join()
            else:
                self.send_chunks()

            self.missing_parts = []

            data = requests.get(self.location)

            if data.text:
                json_data = json.loads(data.text)
                if 'missing_parts' in json_data and json_data['missing_parts']:
                    self.missing_parts = json_data['missing_parts']
                    self.missing_parts.reverse()
                    raise TelestreamCloudException('Failed to upload some parts, missing parts: %s' % self.missing_parts)
        else:
            raise KeyError("Already started")


    def resume(self):
        if self.status != 'uploaded':
            self.start()
        else:
            raise TelestreamCloudException('File already uploaded')


    def abort(self):
        if self.status != 'uploaded':
            self.status = 'aborted'
            self.error_message = None
            res = requests.delete(self.location)
        else:
            raise TelestreamCloudException('File already uploaded')
