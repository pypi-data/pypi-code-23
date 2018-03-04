from .ast import Ast

class TokenType(object):
    
    def __init__(self, token_type, id=""):
        self._token_type = token_type
        self._id = id
    
    def translate(self, grammar, token_stream):
        if not token_stream.has_next():
            return None # <- translation failed
        token = token_stream.peek()
        if self._token_type in token.types:
            token_stream.advance()
            return [Ast(self._token_type, token.value, self._id)]
        else:
            return None # <- translation failed
    
class Rule(object):
    
    def __init__(self, name, id=""):
        self._name = name
        self._id = id
        
    def translate(self, grammar, token_stream):
        translator = grammar.get_rule(self._name)
        nodes = translator.translate(grammar, token_stream)
        if nodes is not None:
            ast = Ast(self._name, id=self._id)
            for node in nodes:
                ast.add_child(node)
            trans = grammar.get_ast_transform(self._name)
            if trans:
                ast = trans(ast)
                ast.id = self._id
            if self._name == grammar.get_root_rule():
                ast.set_attr("root", "true")
            return [ast]
        else:
            return None
    
class Sequence(object):
    
    def __init__(self, *elements):
        self._elements = elements
        
    def translate(self, grammar, token_stream):
        ret = []
        token_stream.open_transaction()
        for element in self._elements:
            nodes = element.translate(grammar, token_stream)
            if nodes is None:
                token_stream.undo()
                return None
            ret += nodes
        token_stream.commit()
        return ret
    
class OneOf(object):
    
    def __init__(self, *choices):
        self._choices = choices
        
    def translate(self, grammar, token_stream):
        token_stream.open_transaction()
        for choice in self._choices:
            nodes = choice.translate(grammar, token_stream)
            if nodes is not None:
                token_stream.commit()
                return nodes
        token_stream.undo()
        return None

class Optional(object):
    
    def __init__(self, translator):
        self._translator = translator
        
    def translate(self, grammar, token_stream):
        return self._translator.translate(grammar, token_stream) or []
        
class Many(object):
    
    def __init__(self, translator):
        self._translator = translator
        
    def translate(self, grammar, token_stream):
        ret = []
        while True:
            nodes = self._translator.translate(grammar, token_stream)
            if nodes is not None:
                ret += nodes
            else:
                break
        return ret
    
class OneOrMore(object):
    
    def __init__(self, translator):
        self._translator = translator
        
    def translate(self, grammar, token_stream):
        ret = []
        nodes = self._translator.translate(grammar, token_stream)
        if nodes is None:
            return None
        ret += nodes
        while True:
            nodes = self._translator.translate(grammar, token_stream)
            if nodes is not None:
                ret += nodes
            else:
                break
        return ret
                
