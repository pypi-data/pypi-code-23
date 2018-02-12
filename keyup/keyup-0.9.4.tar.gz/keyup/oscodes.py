"""
Standard OS Module Exit Codes
    - See https://docs.python.org/3.6/library/os.html#process-management
"""
import os

exit_codes = {
    'EX_OK': {
        'Code': 0,
        'Reason': 'No error occurred'
    },
    'E_DEPENDENCY': {
        'Code': 1,
        'Reason': 'Missing required dependency'
    },
    'E_DIR': {
        'Code': 2,
        'Reason': 'Failure to create log dir, log file'
    },
    'E_ENVIRONMENT': {
        'Code': 3,
        'Reason': 'Incorrect shell, language interpreter, or operating system'
    },
    'EX_AWSCLI': {
        'Code': 4,
        'Reason': 'Value could not be determined from local awscli configuration'
    },
    'EX_NOPERM': {
        'Code': os.EX_NOPERM,
        'Reason': 'IAM user or role permissions do not allow this action'
    },
    'E_AUTHFAIL': {
        'Code': 5,
        'Reason': 'Authentication Fail'
    },
    'E_BADPROFILE': {
        'Code': 6,
        'Reason': 'Local profile variable not set or incorrect'
    },
    'E_USER_CANCEL': {
        'Code': 7,
        'Reason': 'User abort'
    },
    'E_BADARG': {
        'Code': 8,
        'Reason': 'Bad input parameter'
    },
    'E_EXPIRED_CREDS': {
        'Code': 9,
        'Reason': 'Credentials expired or otherwise no longer valid'
    },
    'E_MISC': {
        'Code': 9,
        'Reason': 'Unknown Error'
    },
    'EX_NOUSER': {
        'Code': os.EX_NOUSER,
        'Reason': 'specified user does not exist'
    },
    'EX_CONFIG': {
        'Code': os.EX_CONFIG,
        'Reason': 'Configuration or config parameter error'
    },
    'EX_CREATE_FAIL': {
        'Code': 21,
        'Reason': 'Keyset failed to create. Possible Permissions issue'
    },
    'EX_DELETE_FAIL': {
        'Code': 22,
        'Reason': 'Keyset failed to delete.  Possible Permissions issue'
    }
}


"""
os.EX_DATAERR

    Exit code that means the input data was incorrect.
    Availability: Unix.

os.EX_NOINPUT

    Exit code that means an input file did not exist or was not readable.
    Availability: Unix.

os.EX_NOHOST

    Exit code that means a specified host did not exist.
    Availability: Unix.

os.EX_UNAVAILABLE

    Exit code that means that a required service is unavailable.
    Availability: Unix.

os.EX_SOFTWARE

    Exit code that means an internal software error was detected.
    Availability: Unix.

os.EX_OSERR

    Exit code that means an operating system error was detected, such as the inability to fork or create a pipe.
    Availability: Unix.

os.EX_OSFILE

    Exit code that means some system file did not exist, could not be opened, or had some other kind of error.
    Availability: Unix.

os.EX_CANTCREAT

    Exit code that means a user specified output file could not be created.
    Availability: Unix.

os.EX_IOERR

    Exit code that means that an error occurred while doing I/O on some file.
    Availability: Unix.

os.EX_TEMPFAIL

    Exit code that means a temporary failure occurred. This indicates something that may not really be an error, such as a network connection that couldn’t be made during a retryable operation.
    Availability: Unix.

os.EX_PROTOCOL

    Exit code that means that a protocol exchange was illegal, invalid, or not understood.
    Availability: Unix.

os.EX_NOTFOUND

    Exit code that means something like “an entry was not found”.
    Availability: Unix.
"""
