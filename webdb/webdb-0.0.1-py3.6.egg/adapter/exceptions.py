
class Error(BaseException):
	pass

class DatabaseError(Error):
	pass


class InterfaceError(Error):
	pass
class DataError(Error):
	pass
class OperationalError(Error):
	pass
class IntegretyError(Error):
	pass
class ProgrammingError(Error):
	pass
class NotSupportedError(Error):
	pass
