"""
JIM protocol config file.
"""

# DEBUG_MODE may be:
# 0 - Do not show messages
# 1 - Show send_message() and get_message()
# 2 - Show Enter and Return in get_message()
DEBUG_MODE = 1
ENCODING = 'utf-8'

# Keys
ACTION = 'action'
TIME = 'time'
TYPE = 'type'
USER = 'user'
ACCOUNT_NAME = 'account_name'
USER_ID = 'user_id'
PASSWORD = 'password'
TO = 'to'
FROM = 'from'
MESSAGE = 'message'
ROOM = 'room'
RESPONSE = 'response'
ALERT = 'alert'
ERROR = 'error'
QUANTITY = 'quantity'

# Values
PRESENCE = 'presence'
PROBE = 'probe'
MSG = 'msg'
QUIT = 'quit'
JOIN = 'join'
LEAVE = 'leave'
AUTHENTICATE = 'authenticate'
STATUS = 'status'  # also is key for USER
GET_CONTACTS = 'get_contacts'
CONTACT_LIST = 'contact_list'
ADD_CONTACT = 'add_contact'
DEL_CONTACT = 'del_contact'

# Response codes
BASIC_NOTICE = 100
IMPORTANT_NOTICE = 101
OK = 200
CREATED = 201
ACCEPTED = 202
WRONG_REQUEST = 400  # or JSON object
NOT_AUTHORIZED = 401
WRONG_LOGIN_OR_PASSWORD = 402
FORBIDDEN = 403
NOT_FOUND = 404
CONFLICT = 409
GONE = 410
SERVER_ERROR = 500

# Tuple of actions
ACTIONS = (PRESENCE, PROBE, MSG, QUIT, JOIN, LEAVE, AUTHENTICATE, STATUS,
           GET_CONTACTS, CONTACT_LIST, ADD_CONTACT, DEL_CONTACT
)

# Tuple of response codes
RESPONSE_CODES = (
    BASIC_NOTICE, IMPORTANT_NOTICE, OK, CREATED, ACCEPTED, WRONG_REQUEST, NOT_AUTHORIZED,
    WRONG_LOGIN_OR_PASSWORD, FORBIDDEN, NOT_FOUND, CONFLICT, GONE, SERVER_ERROR
)

USERNAME_MAX_LENGTH = 25
ROOMNAME_MAX_LENGTH = 25
MESSAGE_MAX_LENGTH = 1000
PASSWORD_MAX_LENGTH = 32