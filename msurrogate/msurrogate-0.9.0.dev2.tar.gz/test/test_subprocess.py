"""
"""
from __future__ import division, print_function, unicode_literals

from msurrogate.subproc_server import ServerSubprocess


if __name__ == "__main__":
    app = ServerSubprocess(
        module_name = 'msurrogate.ping_test',
    )
    print("SECRET: ", app.mysecret)
    print(app.cookie_dict)

