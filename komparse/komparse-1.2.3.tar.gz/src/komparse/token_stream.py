class TokenStream(object):
    
    def __init__(self, tokens):
        self._remaining = tokens[:]
        self._remaining.reverse()
        self._consumption = [[]]
        
    def has_next(self):
        return bool(self._remaining)
    
    def peek(self):
        return self._remaining[-1]
    
    def advance(self):
        ret = self._remaining.pop()
        self._consumption[-1].append(ret)
        return ret
    
    def open_transaction(self):
        self._consumption.append([])
    
    def commit(self):
        if len(self._consumption) == 1:
            raise Exception("Commit not allowed")
        self._consumption[-1] +=  self._consumption.pop()
        
    def undo(self):
        if len(self._consumption) == 1:
            raise Exception("Cannot be undone")
        consumed = self._consumption.pop()
        while consumed:
            self._remaining.append(consumed.pop())
            