class NotsError(Exception):
    pass


class MissingConvertorError(NotsError):
    pass


class ConvertError(NotsError):
    pass
