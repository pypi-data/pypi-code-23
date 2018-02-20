'''Validation-related stuff'''
# ------------------------------------------------------------------------------
from appy.px import Px

# ------------------------------------------------------------------------------
class Errors:
    '''When validation errors are encountered, they are stored on an instance of
       this class. For example, if an error occurrs on field named "field1", an
       attribute named "field1" will be stored on this instance, holding
       translated error message.'''

    px = Px('''
     <table class="grid compact"
            style="margin-top:10px; text-align:left" width="100%">
      <tr><th width="25%">:_('field_name')</th><th>:_('error_name')</th></tr>
      <tr for="message, fieldLabels in errors.getAll(obj)">
       <td>::fieldLabels</td><td>:message</td></tr>
     </table>''')

    def __nonzero__(self): return bool(self.__dict__)
    def get(self, name, default=None): return getattr(self, name, default)

    def getAll(self, obj):
        '''Returns the list of all errors, grouped by message: if the same error
           message concerns several fields, a single entry is inserted in the
           list.'''
        r = {} # ~{s_message: s_fieldLabels}~
        compound = [] # Add a summarized message for compound fields
        for name, message in self.__dict__.iteritems():
            if '*' in name:
                name = name.split('*', 1)[0]
                if name in compound: continue
                compound.append(name)
                # Do not show the detailed message
                message = obj.translate('validation_sub_error')
            # Get the translated label
            text = obj.translate(obj.getField(name).labelId)
            # Insert the message into the result
            if message not in r:
                r[message] = text
            else:
                r[message] += '<br/>%s' % text
        return r.items()
# ------------------------------------------------------------------------------
