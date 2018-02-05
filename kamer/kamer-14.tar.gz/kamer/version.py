# kamer/version.py
#
#

""" version plugin. """

from kamer import __version__

txt = """ straffeloosheid verzekerende kamerleden de cel in ! """

def version(event):
    event.reply("KAMER #%s - %s" % (__version__, txt))
