def get_domain_from_email_address(email_address):
    domain = email_address.split('@')[-1]
    return domain


def tokenize_keywords(keywords):
    sanitized = keywords.replace(', ', ',').replace(' ,', ',').strip(' ,')
    return sanitized.split(',')
