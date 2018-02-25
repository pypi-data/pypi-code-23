class _HttpNext:
    req = []
    res = []
    callbacks = []

    def append(self, req, res, callback):
        self.req.append(req)
        self.res.append(res)
        self.callbacks.append(callback)

    def _remove_first(self):
        if len(self.req) > 0:
            self.req.pop(0)
            self.res.pop(0)
            self.callbacks.pop(0)

    def _invoke_first(self):
        if len(self.req) > 0:
            callback = self.callbacks[0]
            req = self.req[0]
            res = self.res[0]
            self._remove_first()
            callback(
                req,
                res,
                self.next
            )

    def has_next(self):
        return len(self.callbacks) > 0

    def next(self):
        if self.has_next():
            self._invoke_first()
            return True
        else:
            return False
