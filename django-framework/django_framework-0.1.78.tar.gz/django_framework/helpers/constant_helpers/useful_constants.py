

ALLOWED_TRUE_VALUES = ('true', 'True', 1, '1', 'TRUE',  True)

ALLOWED_FALSE_VALUES = ('false', 'False', 0, '0', 'FALSE', False)

ALLOWED_NONE_VALUES = ('null', 'Null' 'none', 'None', 'NONE', None)

ALLOWED_BLANK_VALUES = ('', None)


def check_is_blank(value, fail_silently = True):
    if value in ALLOWED_BLANK_VALUES:
        return True
    
    if fail_silently:
        return False
    
    raise ValueError('Expected a value that can be parsed to blank')


def check_is_true(value, fail_silently = True):
    if value in ALLOWED_TRUE_VALUES:
        return True
    
    if fail_silently:
        return False
    
    raise ValueError('Expected a value that can be parsed to True')
    
    
def check_is_false(value, fail_silently = True):
    if value in ALLOWED_FALSE_VALUES:
        return True
    
    if fail_silently:
        return False
    
    raise ValueError('Expected a value that can be parsed to True')
    
def check_is_none(value, fail_silently = True):
    if value in ALLOWED_NONE_VALUES:
        return True
    
    if fail_silently:
        return False
    
    raise ValueError('Expected a value that can be parsed to True')