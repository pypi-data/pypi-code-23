import requests
from pathlib import Path
import itertools


class CFR(object):
    celeb_url: str = "https://openapi.naver.com/v1/vision/celebrity"
    face_sensing_url: str = "https://openapi.naver.com/v1/vision/face"

    def __init__(self, client_id: str, client_secret: str):
        self.client_id = client_id
        self.client_secret = client_secret
        self.headers = {
            "X-Naver-Client-Id": self.client_id,
            "X-Naver-Client-Secret": self.client_secret
        }

    def get_celeb_similarity(self, file_path: Path) -> dict:
        return self.get_info(file_path, self.celeb_url)

    def get_bulk_celeb_similarity(self, file_path: Path) -> list:
        return self.get_bulk_info(file_path, self.get_celeb_similarity)

    def get_face_sensing_info(self, file_path: Path) -> dict:
        return self.get_info(file_path, self.face_sensing_url)

    def get_bulk_face_sensing_info(self, file_path: Path) -> list:
        return self.get_bulk_info(file_path, self.get_face_sensing_info)

    def get_info(self, file_path: Path, url: str):
        if not file_path.exists():
            print("file path not exist")
            raise FileExistsError
        file = {'image': open(file_path, 'rb')}
        response = requests.post(url=url, headers=self.headers, files=file)
        rescode = response.status_code
        if rescode != 200:
            print("Error Code:" + rescode)
        return response.json()

    def get_bulk_info(self, file_path: Path, func) -> list:
        if not file_path.exists():
            print("file path not exist")
            raise FileExistsError
        file_types = [f"**/*.{file_type}" for file_type in ["jpg", "jpeg", "png"]]

        files = list(itertools.chain.from_iterable(
            list(map(lambda f: file_path.glob(f), file_types)))
        )

        if len(files) == 0:
            print("There is no Image File")
            raise FileExistsError
        return [func(Path(str(file))) for file in files]
