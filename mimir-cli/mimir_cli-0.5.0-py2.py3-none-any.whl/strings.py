"""
strings for the mimir cli
"""
import os


MIMIR_DIR = os.path.expanduser('~/.mimir/')
ZIP_LOC = '{}sub.zip'.format(MIMIR_DIR)

API_URL = 'https://app.mimir.cloud'
API_SUBMIT_URL = '{base_url}/lms/projects/{{}}/project_submissions'.format(base_url=API_URL)
API_LOGIN_URL = '{base_url}/lms/user_sessions'.format(base_url=API_URL)
CLASSROOM_URL = 'https://class.mimir.io'

AUTH_SUCCESS = 'Successfully logged into Mimir Classroom!'
LOGOUT_SUCCESS = 'Successfully logged out of Mimir Classroom!'

ERR_NOT_AUTH = 'Please log into Mimir Classroom first!'
ERR_INVALID_CRED = 'Invalid email or password!'
ERR_INVALID_FILE = 'Failed to open file `{}`.'

PROJECT_PROMPT = 'Type the number of the project you want to submit to'
PROJECT_ERR_0_TO_N = 'Input a number 0 through {} please!'

EMAIL_PROMPT = 'Email'
EMAIL_HELP = 'Mimir Classroom Email'
PASSWORD_HELP = 'Mimir Classroom Password'


SUB_WARNING = '\nWARNING'
SUB_CONFIRM_FORCE = 'Would you still like to submit?'
SUB_SUCCESS_URL = (
    'Submission sucessful! Click here for your results: {}/project_submissions/{{}}'.format(
        CLASSROOM_URL
    )
)
