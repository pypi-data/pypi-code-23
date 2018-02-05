"""
"""
from __future__ import division, print_function, unicode_literals
from msurrogate import SurrogateApp


def test_ping(text = ''):
    print("PONG" + text)


if __name__ == "__main__":
    app = SurrogateApp()
    app.option('serializer-preferred', 'dill')
    metaD = app.meta_daemon_setup()
    metaD.register(test_ping)
    app.run_loop()

