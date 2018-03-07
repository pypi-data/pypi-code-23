def ensure_unicode(s):
    try:
        return s.decode('utf8')
    except UnicodeEncodeError:
        return s.encode('utf8').decode('utf8')
