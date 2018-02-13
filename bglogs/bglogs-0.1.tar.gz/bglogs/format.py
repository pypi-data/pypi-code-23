import logging


class BGFmt(logging.Formatter):

    def __init__(self):
        super().__init__(fmt='%(asctime)s %(name)s %(levelname)s -- %(message)s', datefmt ='%Y-%m-%d %H:%M:%S')


class FullFmt(logging.Formatter):

    def __init__(self):
        super().__init__(fmt='%(asctime)s  %(name)s %(levelname)s: %(message)s')


class BasicFmt(logging.Formatter):

    def __init__(self):
        super().__init__(fmt='%(levelname)s: %(message)s')
