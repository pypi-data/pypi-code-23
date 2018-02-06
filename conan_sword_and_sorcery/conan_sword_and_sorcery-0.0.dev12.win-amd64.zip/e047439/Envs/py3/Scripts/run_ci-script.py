#!C:\Users\e047439\Envs\py3\Scripts\python.exe
# EASY-INSTALL-ENTRY-SCRIPT: 'conan-sword-and-sorcery==0.0.dev12','console_scripts','run_ci'
__requires__ = 'conan-sword-and-sorcery==0.0.dev12'
import re
import sys
from pkg_resources import load_entry_point

if __name__ == '__main__':
    sys.argv[0] = re.sub(r'(-script\.pyw?|\.exe)?$', '', sys.argv[0])
    sys.exit(
        load_entry_point('conan-sword-and-sorcery==0.0.dev12', 'console_scripts', 'run_ci')()
    )
