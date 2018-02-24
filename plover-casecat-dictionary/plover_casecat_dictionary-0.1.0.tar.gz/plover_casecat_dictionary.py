from plover.steno_dictionary import StenoDictionary
from plover.steno import normalize_steno
from plover import resource
from struct import unpack
import re

KEYS = 'STKPWHRAO*EUFRPBLGTSDZ'

# I admit this is a wild guess
ENCODING = 'latin-1'

def _tidy_translation(t):

    result = t.decode(ENCODING)

    curly_brackets = False

    # these codes have been figured out
    # by inspecting saved dictionaries;
    # they may be wrong.

    if result.startswith('\x10\x81'):
        # prefix
        result = '^' + result
        curly_brackets = True

    if result.endswith('\x10\x01'):
        # suffix
        result = result + '^'
        curly_brackets = True

    if '\x0E' in result:
        # cap up
        result += '{-|}'

    if curly_brackets:
        result = '{'+result+'}'

    result = re.sub(r'[^ -~]', '', result)
    return result

class CaseCatDictionary(StenoDictionary):

    def __init__(self):
        super(CaseCatDictionary, self).__init__()
        self._contents = None
        self._reverse_contents = None
        self.readonly = True

    def getattr(self, key, default=None):
        return self.__getattr__(key, default)

    def _load(self, filename):
        self._contents = {}
        self._reverse_contents = {}

        with open(filename, 'rb') as f:

            f.seek(0x280)

            while True:

                unknown1 = f.read(18)
                if unknown1 is None or len(unknown1)!=18:
                    return

                stroke_count = unpack(">B", f.read(1))[0]
                letter_count = unpack(">B", f.read(1))[0]

                unknown2 = f.read(1)

                stroke = []

                for i in range(stroke_count):
                    stroke.append('')

                    stroke_bits = unpack(">L", f.read(4))[0]

                    for k in range(len(KEYS)):

                        bit = (0x80000000) >> k
                        if KEYS[k]=='*' and stroke[-1]=='':
                            stroke[-1] += '-'

                        if stroke_bits & bit:
                            stroke[-1] += KEYS[k]

                translation = _tidy_translation(f.read(letter_count))

                key = '/'.join(stroke)

                self._contents[key] = translation
                self._reverse_contents[translation] = key

                padding_space = f.tell()%4
                if padding_space != 0:
                    f.read(4-padding_space)

    def __setitem__(self, key, value):
        raise NotImplementedError()

    def __delitem__(self, key):
        raise NotImplementedError()

    def __getitem__(self, key):
        return self._contents.__getitem__(key)

    def get(self, item, key, fallback=None):
        return self._contents.get(item, key, fallback)

    def reverse_lookup(self, value):
        return self._reverse_contents[value]
