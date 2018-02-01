

class SessionException(Exception):
    """
.. class:: SlaveException(Exception)

    Base exception raised for error conditions when interacting with the modem
    """
    pass


class CRCException(SessionException):
    """
.. class:: CRCError(SlaveException)

    Raised when the CRC in message does not match the reported CRC on the message
    """
    pass
