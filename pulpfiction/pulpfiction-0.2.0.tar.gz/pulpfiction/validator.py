from langdetect import detect_langs
from langdetect.lang_detect_exception import LangDetectException

from .models import Comment


class Comment:
    MIN_DETECTION_CONFIDENCE = 0.90

    def __init__(self, comment: Comment, language_code: str='en') -> None:
        self.comment = comment
        self.language_code = language_code
        self.language_code_detected = None

    def is_valid(self) -> bool:
        try:
            self.validate()
        except AssertionError:
            return False
        else:
            return True

    def validate(self) -> None:
        try:
            guess = detect_langs(self.comment.text)[0]
        except (IndexError, LangDetectException):
            # skip validation since we cannot guess the language code
            return
        else:
            self.language_code_detected = guess.lang
            if float(guess.prob) < self.MIN_DETECTION_CONFIDENCE:
                return

            assert self.language_code_detected == self.language_code

    def __bool__(self) -> bool:
        return self.is_valid()
