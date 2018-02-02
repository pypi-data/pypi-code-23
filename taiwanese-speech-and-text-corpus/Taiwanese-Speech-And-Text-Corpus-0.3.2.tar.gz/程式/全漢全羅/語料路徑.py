import os


class 語料路徑:
    @classmethod
    def _這馬所在(cls):
        return os.path.join(os.path.dirname(__file__), '語料')

    @classmethod
    def 原始一對一語料(cls):
        return os.path.join(cls._這馬所在(), '語句文本.txt.gz')

    @classmethod
    def 斷詞典(cls):
        return os.path.join(cls._這馬所在(), '本調變調詞典.pickle.gz')

    @classmethod
    def 斷詞語言模型(cls):
        return os.path.join(cls._這馬所在(), '語言模型.lm')
