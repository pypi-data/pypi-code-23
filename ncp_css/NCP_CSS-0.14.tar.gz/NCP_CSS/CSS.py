import requests
from pathlib import Path


class CSS(object):
    """
    jinho : 한국어, 남성 음색
    clara : 영어, 여성 음색
    matt : 영어, 남성 음색
    yuri : 일본어, 여성 음색
    shinji : 일본어, 남성 음색
    meimei : 중국어, 여성 음색
    liangliang : 중국어, 남성 음색
    jose : 스페인어, 남성 음색
    carmen : 스페인어, 여성 음색
    """
    speaker_list: list = ["mijin", "jinho", "clara", "matt", "yuri", "shinji", "meimei", "liangliang", "jose", "carmen"]
    css_url: str = "https://openapi.naver.com/v1/voice/tts.bin"
    min_speed, max_speed = -5, 5

    def __init__(self, client_id: str, client_secret: str):
        self.client_id = client_id
        self.client_secret = client_secret
        self.headers = {
            "X-Naver-Client-Id": self.client_id,
            "X-Naver-Client-Secret": self.client_secret
        }

    # possible lang : ko, eg, ja, zh, zh-CN
    def translate_text(self, text: str, file_path: Path = Path.cwd() / "result.mp3", speaker: str = "mijin", speed=0):
        if text is None:
            raise ValueError("you should input text")

        if speaker not in CSS.speaker_list:
            raise ValueError(f"'speaker should be one of [{CSS.speaker_list}]'")
        if CSS.min_speed > speed or CSS.max_speed < speed:
            print(CSS.min_speed > speed)
            print(CSS.max_speed < speed)
            raise ValueError(f"speed range should be {CSS.min_speed} ~ {CSS.max_speed}")

        data: dict = {
            "speaker": speaker,
            "speed": speed,
            "text": text,
        }

        result = requests.post(url=CSS.css_url, headers=self.headers, data=data)
        if result.status_code == 200:
            response_body = result.content
            with open(file_path, 'wb') as f:
                f.write(response_body)
        else:
            print("Error Code:" + str(result.status_code))
            print(result.headers)
            print(result.text)

    def translate_file(self, text_file: Path, file_path: Path = Path.cwd() / "result.mp3", speaker: str = "mijin",
                       speed=0):
        if text_file is None:
            raise ValueError("you should input text")

        with open(text_file, mode="r", encoding="utf-8") as f:
            text = "".join(f.readlines())
            self.translate_text(text=text, file_path=file_path, speaker=speaker)