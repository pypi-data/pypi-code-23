import os
import logging
import colorama


LOGORAMA_DEFAULT_LEVEL = logging.INFO

LOGORAMA_DISABLE_COLORS = os.getenv("COLORAMA_DISABLE_COLORS")
LOGORAMA_DISABLE_COLORS = True if LOGORAMA_DISABLE_COLORS == "true" else False

LOGORAMA_TZ = "US/Central"

LOGORAMA_COLORS = {
    'WARNING': colorama.Fore.YELLOW,
    'INFO': colorama.Fore.GREEN,
    'DEBUG': colorama.Fore.CYAN,
    'ERROR': colorama.Fore.RED + colorama.Style.BRIGHT,
    'CRITICAL': colorama.Fore.WHITE + colorama.Back.RED
}

LOGORAMA_DEFAULT_FORMAT = '%(asctime)s - [%(levelname)s] - ' \
                          '{%(name)s:%(funcName)s:%(lineno)s} - %(message)s'
