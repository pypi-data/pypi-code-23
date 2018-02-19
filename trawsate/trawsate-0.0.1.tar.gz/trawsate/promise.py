# -*- coding: utf-8 -*-
from typing import Optional, TypeVar, Generic

T = TypeVar('T')


class Promise(Generic[T]):
    """
    Represents the result of a job's execution, both success and failure.
    """

    @property
    def ok(self) -> bool:
        """
        Find whether this promise is fulfilled.

        :return: True if it is (and there's a result), false otherwise (and
                 there's an exception).
        """
        return self._exception is None

    @staticmethod
    def fulfilled(result: T) -> 'Promise[T]':
        """
        Create a new succeeded promise.

        :param result: The successful result.
        """
        return Promise(result=result)

    @staticmethod
    def rejected(exception: Exception) -> 'Promise[T]':
        """
        Create a new rejected promise.

        :param exception: The reason for failure
        """
        return Promise(exception=exception)

    def __init__(self, result: Optional[T] = None,
                 exception: Optional[Exception] = None):
        """
        Initialise a new promise.

        :param result: If successful, the result.
        :param exception: If unsuccessful, the exception.
        """
        self._result = result
        self._exception = exception

    def __str__(self) -> str:
        if self.ok:
            return 'ok'
        return str(self._exception)
