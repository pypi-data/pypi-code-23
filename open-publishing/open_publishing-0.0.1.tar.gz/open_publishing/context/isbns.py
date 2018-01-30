class Isbns(object):
    def __init__(self,
                 context):
        self._ctx = context

    def allocate(self,
                 prefix):
        self._ctx.gjp.allocate_isbns_block(prefix)
        
