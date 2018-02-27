# -*- coding: utf-8 -*-
"""

This module is responsible for handling every exception that occurs
in the application, using a wrapper class, which is used to wrap a
group of exceptions in python.


Their specification is only logical and is not related to any language
specifications.

"""

import logging


# This is base class for app exceptions.
class ErrorWrapper(Exception):
    """ This is base class for my application exceptions.

    This class wraps every defined exception in python for user
    message construction and logging issues.

    Attributes:
    ----------
    ex : str
        The exception type defined by its class name.
    code : int
        The package specific exception code.

    """
    def __init__(self, ex=None, code=None):
        """
        Initializer for ErrorWrapper class.


        Parameters
        ----------
        ex : Exception
            The exception object.

        code : int
            The exception code.

        """
        self.ex = ex
        self.code = code
        logging.basicConfig(filename='base_log.log', format='%(asctime)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p')

    def get_code(self):
        """
        This function gets the specific error code for error handling.


        Parameters
        ----------

        Returns
        -------
        int
            The error code.

        """
        if FileError(self.ex).check():
            return FileError(self.ex).codec()
        elif OperationError(self.ex).check():
            return OperationError(self.ex).codec()
        elif ImportsError(self.ex).check():
            return ImportsError(self.ex).codec()
        elif IndexingError(self.ex).check():
            return IndexingError(self.ex).codec()
        else:
            return -1

    def handle(self):
        """
        This function delegates errors handling to defined-error classes according to their code.


        Parameters
        ----------

        Returns
        -------
        str
            The user error message.

        """
        if self.code is None:
            self.code = self.get_code()
        if self.code == -1:
            return OtherError(self.ex, self.code).handle_msg()
        elif self.code / 10 == 1:
            return FileError(self.ex, self.code).handle_msg()
        elif self.code / 10 == 2:
            return OperationError(self.ex, self.code).handle_msg()
        elif self.code / 10 == 3:
            return ImportsError(self.ex, self.code).handle_msg()
        elif self.code / 10 == 4:
            return IndexingError(self.ex, self.code).handle_msg()
        elif self.code / 10 == 5:
            return ParametersError(self.ex, self.code).handle_msg()
        else:
            return OtherError(self.ex, -1).handle_msg()


# This class wraps file errors.
class FileError(ErrorWrapper):
    """ This is base class for my application file exceptions.

    This class wraps every defined file exception in python for user
    message construction and logging issues.

    """
    def __init__(self, ex=None, code=None):
        """
        Initializer for FileError class.


        Parameters
        ----------
        ex : Exception
            The exception object.

        code : int
            The exception code.

        """
        if ex is not None:
            if code is not None:
                super(FileError, self).__init__(ex, code)
            else:
                super(FileError, self).__init__(ex)
        else:
            if code is not None:
                super(FileError, self).__init__(Exception(), code)
            else:
                super(FileError, self).__init__()

    def _get_file_name(self):
        """
        This function gets the path of the file that caused the exception.


        Parameters
        ----------

        Returns
        -------
        str
            The erroneous file path.

        """
        exception_message = self.ex.__str__()
        words = exception_message.split(" ")
        return words[len(words)-1]

    def check(self):
        """
        This function checks the exception type to determine if it should be handled by FileError class.


        Parameters
        ----------

        Returns
        -------
        bool
            True if the exception should be handled by FileError class.

        """
        if len(self.ex.args) > 1:
            return True
        else:
            return False

    def codec(self):
        """
        This function gets the specific FileError code.


        Parameters
        ----------

        Returns
        -------
        int
            The FileError code.

        """
        if self.ex.args[1] == "No such file or directory":
            return 10
        elif self.ex.args[1] == "Permission denied":
            return 11
        else:
            return 12

    def handle_msg(self):
        """
        This function logs the error in the log file and constructs an error message for the user.


        Parameters
        ----------

        Returns
        -------
        str
            The user error message.

        """
        if self.code == 10:
            logging.getLogger("FileError").error(" error[" + str(self.code) + "] " + self.ex.args[1] + ": " + self._get_file_name())
            return "error[" + str(self.code) + "] file not found at: " + self._get_file_name()
        elif self.code == 11:
            logging.getLogger("FileError").error(" error[" + str(self.code) + "] " + self.ex.args[1] + ": " + self._get_file_name())
            return "error[" + str(self.code) + "] permissions to access file denied at: " + self._get_file_name()
        else:
            logging.getLogger("FileError").error(" error[" + str(self.code) + "] " + self.ex.args[1] + ": " + self._get_file_name())
            return "error[" + str(self.code) + "] unknown IOError at: " + self._get_file_name()


# This class wraps operations errors.
class OperationError(ErrorWrapper):
    """ This is base class for my application operations exceptions.

    This class wraps every defined operation exception in python for user
    message construction and logging issues.

    """
    def __init__(self, ex=None, code=None):
        """
        Initializer for OperationError class.


        Parameters
        ----------
        ex : Exception
            The exception object.

        code : int
            The exception code.

        """
        if ex is not None:
            if code is not None:
                super(OperationError, self).__init__(ex, code)
            else:
                super(OperationError, self).__init__(ex)
        else:
            if code is not None:
                super(OperationError, self).__init__(Exception(), code)
            else:
                super(OperationError, self).__init__()

    def check(self):
        """
        This function checks the exception type to determine if it should be handled by OperationError class.


        Parameters
        ----------

        Returns
        -------
        bool
            True if the exception should be handled by OperationError class.

        """
        if self.ex.__class__ is ZeroDivisionError or self.ex.__class__ is OverflowError or self.ex.__class__ is MemoryError:
            return True
        else:
            return False

    def codec(self):
        """
        This function gets the specific OperationError code.


        Parameters
        ----------

        Returns
        -------
        int
            The OperationError code.

        """
        if self.ex is OverflowError:
            return 20
        elif self.ex is MemoryError:
            return 21
        else:
            return 22

    def handle_msg(self):
        """
        This function log the error in the log file and constructs an error message for the user.


        Parameters
        ----------

        Returns
        -------
        str
            The user error message.

        """
        if self.code == 20:
            logging.getLogger("OperationError").error(" error[" + str(self.code) + "] " + self.ex.args[0])
            return "error[" + str(self.code) + "] " + self.ex.args[0]
        elif self.code == 21:
            logging.getLogger("OperationError").error(" error[" + str(self.code) + "] " + self.ex.args[0])
            return "error[" + str(self.code) + "] " + self.ex.args[0]
        elif self.code == 22:
            logging.getLogger("OperationError").error(" error[" + str(self.code) + "] " + self.ex.args[0])
            return "error[" + str(self.code) + "] " + self.ex.args[0]


# This class wraps imports errors.
class ImportsError(ErrorWrapper):
    """ This is base class for my application imports exceptions.

    This class wraps the defined imports exception in python for user
    message construction and logging issues.

    """
    def __init__(self, ex=None, code=None):
        """
        Initializer for ImportsError class.


        Parameters
        ----------
        ex : Exception
            The exception object.

        code : int
            The exception code.

        """
        if ex is not None:
            if code is not None:
                super(ImportsError, self).__init__(ex, code)
            else:
                super(ImportsError, self).__init__(ex)
        else:
            if code is not None:
                super(ImportsError, self).__init__(Exception(), code)
            else:
                super(ImportsError, self).__init__()

    def check(self):
        """
        This function checks the exception type to determine if it should be handled by ImportsError class.


        Parameters
        ----------

        Returns
        -------
        bool
            True if the exception should be handled by ImportsError class.

        """
        if self.ex.__class__ is ImportError:
            return True
        else:
            return False

    def codec(self):
        """
        This function gets the specific ImportsError code.


        Parameters
        ----------

        Returns
        -------
        int
            The ImportsError code.

        """
        if self.ex.__class__ is ImportError:
            return 30

    def handle_msg(self):
        """
        This function log the error in the log file and constructs an error message for the user.


        Parameters
        ----------

        Returns
        -------
        str
            The user error message.

        """
        if self.code == 30:
            logging.getLogger("ImportsError").error(" error[" + str(self.code) + "] " + self.ex.args[0])
            return "error[" + str(self.code) + "] " + self.ex.args[0]


# This class wraps indexing errors.
class IndexingError(ErrorWrapper):
    """ This is base class for my application indexing exceptions.

    This class wraps every defined indexing exception in python for user
    message construction and logging issues.

    """
    def __init__(self, ex=None, code=None):
        """
        Initializer for IndexingError class.


        Parameters
        ----------
        ex : Exception
            The exception object.

        code : int
            The exception code.

        """
        if ex is not None:
            if code is not None:
                super(IndexingError, self).__init__(ex, code)
            else:
                super(IndexingError, self).__init__(ex)
        else:
            if code is not None:
                super(IndexingError, self).__init__(Exception(), code)
            else:
                super(IndexingError, self).__init__()

    def check(self):
        """
        This function checks the exception type to determine if it should be handled by IndexingError class.


        Parameters
        ----------

        Returns
        -------
        bool
            True if the exception should be handled by IndexingError class.

        """
        if self.ex.__class__ is KeyError or self.ex.__class__ is IndexError:
            return True
        else:
            return False

    def codec(self):
        """
        This function gets the specific IndexingError code.


        Parameters
        ----------

        Returns
        -------
        int
            The IndexingError code.

        """
        if self.ex.__class__ is IndexError:
            return 40
        else:
            return 41

    def handle_msg(self):
        """
        This function log the error in the log file and constructs an error message for the user.


        Parameters
        ----------

        Returns
        -------
        str
            The user error message.

        """
        if self.code is 40:
            logging.getLogger("IndexingError").error(" error[" + str(self.code) + "] " + self.ex.args[0])
            return "error[" + str(self.code) + "] " + self.ex.args[0]
        elif self.code is 41:
            logging.getLogger("IndexingError").error(" error[" + str(self.code) + "] " + self.ex.args[0])
            return "error[" + str(self.code) + "] " + self.ex.args[0]


# This class wraps parameters errors.
class ParametersError(ErrorWrapper):
    """ This is base class for my application parameters exceptions.

    This class wraps every parameters exception in python for user
    message construction and logging issues.

    """

    def __init__(self, ex=None, code=None):
        """
        Initializer for ParametersError class.


        Parameters
        ----------
        ex : Exception
            The exception object.

        code : int
            The exception code.

        """
        if ex is not None:
            if code is not None:
                super(ParametersError, self).__init__(ex, code)
            else:
                super(ParametersError, self).__init__(ex)
        else:
            if code is not None:
                super(ParametersError, self).__init__(Exception(), code)
            else:
                super(ParametersError, self).__init__()

    def check(self):
        """
        This function checks the exception type to determine if it should be handled by ParametersError class.


        Parameters
        ----------

        Returns
        -------
        bool
            True if the exception should be handled by ParametersError class.

        """
        if self.ex.__class__ is ParametersError:
            return True
        else:
            return False

    def codec(self):
        """
        This function gets the specific ParametersError code.


        Parameters
        ----------

        Returns
        -------
        int
            The ParametersError code.

        """
        if self.ex.__class__ is ParametersError:
            return 50

    def handle_msg(self):
        """
        This function log the error in the log file and constructs an error message for the user.


        Parameters
        ----------

        Returns
        -------
        str
            The user error message.

        """
        if self.code is 50:
            logging.getLogger("ParametersError").error(" error[" + str(self.code) + "] " + self.ex.args[0])
            return "error[" + str(self.code) + "] " + self.ex.args[0]


# This class wraps other exceptions.
class OtherError(ErrorWrapper):
    """ This is base class for my application unknown exceptions.

    This class wraps any defined unhandled exception in python for user
    message construction and logging issues.

    """
    def __init__(self, ex=None, code=None):
        """
        Initializer for OtherError class.


        Parameters
        ----------
        ex : Exception
            The exception object.

        code : int
            The exception code.

        """
        if ex is not None:
            if code is not None:
                super(OtherError, self).__init__(ex, code)
            else:
                super(OtherError, self).__init__(ex)
        else:
            if code is not None:
                super(OtherError, self).__init__(Exception(), code)
            else:
                super(OtherError, self).__init__()

    def handle_msg(self):
        """
        This function log the error in the log file and constructs an error message for the user.


        Parameters
        ----------

        Returns
        -------
        str
            The user error message.

        """
        if self.code == -1:
            logging.getLogger("OtherError").error(" error[" + str(self.code) + "] " + self.ex.args[0])
            return "error[" + str(self.code) + "] " + self.ex.args[0]