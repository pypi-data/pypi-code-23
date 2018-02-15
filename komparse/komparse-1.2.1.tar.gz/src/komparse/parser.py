from .scanner import Scanner
from .translators import Rule

class Parser(object):
    
    def __init__(self, grammar):
        self._grammar = grammar
        self._root = Rule(self._grammar.get_root_rule())
        self._scanner = Scanner(self._grammar)
        self._error = ""
        
    def parse(self, source):
        self._error = ""
        token_stream = self._scanner.find_tokens(source)
        nodes = self._root.translate(self._grammar, token_stream)
        if not token_stream.has_next():
            return nodes and nodes[0] or None
        else:
            unexpected_token = token_stream.peek()
            self._error = "Unexpected token: '{}' of types '{}'".format(unexpected_token.value, unexpected_token.types)
            return None
        
    def error(self):
        return self._error
