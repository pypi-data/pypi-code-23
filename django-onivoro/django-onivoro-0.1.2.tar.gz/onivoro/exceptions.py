# coding: utf-8


class SincronizadorException(Exception):
    pass


class TransformacaoException(Exception):
    """
    Exceção lançada por uma transformação do dge.
    """
    pass


class CodigoPerigosoException(TransformacaoException):
    """
    Exceção lançada quando código potencialmente perigoso é detectado.
    """
    pass


class MapeamentoException(Exception):
    pass
