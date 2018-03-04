import os

DATA_ROOT = "data/NLI/data/text/"

NLI_DEV = "index-dev.csv"

ENVIRONMENT = "dev"

DATA_TOKENIZED = "tokenized/"
DATA_ORIGINAL = "original/"

DATA_FORMAT = DATA_TOKENIZED

PROJECT_ROOT = os.getcwd()
LOCAL_DUMP = PROJECT_ROOT + "/dumps/"
LOGIREG_PICKLE = PROJECT_ROOT + "/dumps/logireg.pkl"

CHAR_N_RANGE = (4, 8)
WORD_N_RANGE = (1, 3)
