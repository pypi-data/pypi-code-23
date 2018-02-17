from collections import namedtuple
from .token_stream import TokenStream

Token = namedtuple('Token', 'types value')

class Scanner(object):
    
    def __init__(self, grammar):
        self._grammar = grammar
        
    def find_tokens(self, source):
        tokens = []
        remaining = source
        while remaining:
            token_types, text = self._find_next_token(remaining)
            if text is not None:
                if token_types:
                    tokens.append(Token(token_types, text))
                remaining = remaining[len(text):]
            else:
                break
        if remaining:
            raise Exception("Code could not be resolved: {}".format(remaining))
        return TokenStream(tokens)
    
    def _find_next_token(self, s):
        matches = []
        for name, regex in self._grammar.get_token_patterns():
            m = regex.match(s)
            if m:
                text = m.group(1)
                matches.append((name, text))
        return self._max_munch(sorted(matches, key=lambda it: len(it[1]), reverse=True))
        
    def _max_munch(self, sorted_matches):
        token_types = []
        max_len = None
        max_text = None
        for name, text in sorted_matches:
            if max_len is None:
                max_len = len(text)
                max_text = text
            if len(text) == max_len:
                if name not in [self._grammar.WHITESPACE, self._grammar.COMMENT]:
                   token_types.append(name) 
            else:
                break
        return token_types, max_text
        
                    
                