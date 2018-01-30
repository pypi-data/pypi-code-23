from datetime import datetime, date

def _convert_to_date(value):
    if isinstance(value, str):
        # return datetime.strptime(value, '%Y-%m-%d').date()
        return datetime(*[int(i) for i in value.split('-')]).date()
    elif isinstance(value, date):
        return value
    else :
        raise ValueError("Expected instance of str or datetime.date, got {0}".format(value))
