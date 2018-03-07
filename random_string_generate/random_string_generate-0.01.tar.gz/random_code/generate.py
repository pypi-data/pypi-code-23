import random
import string


def generate_random_code_with(name=None, length=10):
    """

    :param name: the initial name of this random code, could be null.
    :param length: the total length of code.
    :return: random generated code
    """
    def generate(length):
        return ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(length))

    name = name or generate(3)
    random_string = name[0] + generate(length-len(name)) + name[1:]
    return random_string


assert isinstance(generate_random_code_with('LXR', 10), str)
assert len(generate_random_code_with('LXR', 10)) == 10
assert generate_random_code_with('LXR', 10).startswith('L')
assert generate_random_code_with('LXR', 10).endswith('XR')


if __name__ == '__main__':
    print(generate_random_code_with('LXR', 10))