import sys
import src

# Rename the 'src' module to 'infcli'
sys.modules[__name__] = __import__('src')
