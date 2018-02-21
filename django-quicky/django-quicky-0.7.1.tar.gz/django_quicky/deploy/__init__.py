# -*- coding: utf-8 -*-

import os
import random
import warnings


__all__ = ["generate_secret_key", "secret_key_from_file"]


def generate_secret_key():
    """
        Returns a Django secret key.
    """
    source = 'abcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*(-_=+)'
    choices = (random.SystemRandom().choice(source) for i in range(50))
    return ''.join(choices)


def secret_key_from_file(file_path):
    """
        Get the secret key from the given file. If the file doesn't exists,
        generate a secret key, save it in this file, an returns it.
    """

    if not os.path.isfile(file_path):
        with open(file_path, 'w') as f:
            f.write(generate_secret_key())
        warnings.warn("The secret key as been generated. Don't "
                      "forget to add '%s' to you ignore lists." % file_path)

    return open(file_path).read().strip()
