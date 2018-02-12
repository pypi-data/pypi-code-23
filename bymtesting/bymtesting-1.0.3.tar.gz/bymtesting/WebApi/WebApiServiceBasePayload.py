from bymtesting.Lib.JsonBase import *


class Developer(JsonBase):

    def __init__(self, navn):
        self.id = None
        self.navn = navn
