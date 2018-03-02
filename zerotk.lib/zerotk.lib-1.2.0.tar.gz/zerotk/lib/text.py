
def safesplit(text, sep, default='', size=2):
    result = text.split(sep)
    fill_count = size - len(result)
    filler = [default] * fill_count
    return result + filler
