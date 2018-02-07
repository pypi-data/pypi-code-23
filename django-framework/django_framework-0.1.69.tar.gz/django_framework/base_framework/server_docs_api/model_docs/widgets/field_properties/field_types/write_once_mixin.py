
class WriteOnceMixin(object):
    
    def get_write_once(self):
        is_write_once = False
        if self.field_name in self.Serializer.Meta.write_once_fields:
            is_write_once = True
    
        self._is_write_once = is_write_once
        return is_write_once
    
    @property
    def is_write_once(self):
        if hasattr(self, '_'+'is_write_once')  == False:
            self.get_write_once()
        return self._is_write_once
    