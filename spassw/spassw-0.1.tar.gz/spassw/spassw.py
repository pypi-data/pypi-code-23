import string, random

def generate_password(params):
    length = int(params.length)
    space  = string.ascii_letters if params.letters else ''
    space += string.digits        if params.digits else ''
    space += string.punctuation   if params.punctuation else ''
    g = [random.choice(space) for e in range(length)]
    return ''.join(g)