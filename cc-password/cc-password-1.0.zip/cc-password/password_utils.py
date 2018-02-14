import bcrypt


def hash_password(password):
    return bcrypt.hashpw(password.encode('utf8'), bcrypt.gensalt())


def match_password(password, hashed_password):
    canditate = password.encode('utf-8')
    return bcrypt.hashpw(canditate, hashed_password) == hashed_password


def is_valid_password(password):
    return len(password) >= 6