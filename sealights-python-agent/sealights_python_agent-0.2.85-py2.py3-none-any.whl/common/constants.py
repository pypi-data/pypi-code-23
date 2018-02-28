import os
import sys

PREFIX = "sl."
CONFIG_FILE = PREFIX + "config.file"
TOKEN = PREFIX + "token"
TOKEN_FILE = PREFIX + "tokenFile"
TOKEN_FILE2 = "sltoken.txt"
USE_INITIAL_COLOR = PREFIX + "useInitialColor"
BUILD_SESSION_ID = PREFIX + "buildSessionId"
BUILD_SESSION_ID_FILE = "buildSessionId.txt"


TECHNOLOGY = "python"
DEFAULT_ENV = "Unit Tests"
DEFAULT_LAB_ID = "DefaultLabId"
TEST_IDENTIFIER = "x-sl-testid"
PYTHON_FILES_REG = r"^[^.#~!$@%^&*()+=,]+\.pyw?$"  # regex taken from coverage.py for finding python files
INIT_TEST_NAME = "__init"
INITIAL_COLOR = "00000000-0000-0000-0000-000000000000/__init"
MAX_ITEMS_IN_QUEUE = 5000
INTERVAL_IN_MILLISECONDS = 10000
ACTIVE_EXECUTION_INTERVAL_IN_MILLISECONDS = 30000
WINDOWS = sys.platform.startswith('win')
LINUX = sys.platform.startswith("linux")
IN_TEST = os.environ.get("SL_TEST")
DEFAULT_WORKSPACEPATH = os.path.relpath(os.getcwd())

FUTURE_STATEMENTS = {
    "nested_scopes": 0x0010,
    "generators": 0,
    "division": 0x2000,
    "absolute_import": 0x4000,
    "with_statement": 0x8000,
    "print_function": 0x10000,
    "unicode_literals": 0x20000,
}

MESSAGES_CANNOT_BE_NONE = " cannot be 'None'."
