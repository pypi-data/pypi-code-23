# -*- coding: utf-8 -*-


# The standard for printing MAC-48 addresses in human-friendly form is six groups of two hexadecimal digits,
# separated by hyphens - or colons :.
MAC = r'^([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})$'

IPV4 = r"^(([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])\.){3}([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])$"


# RFC 1123: http://tools.ietf.org/html/rfc1123
# RFC 952 specified that hostname segments could not start with a digit.
HOSTNAME = r"^(([a-zA-Z0-9]|[a-zA-Z0-9][a-zA-Z0-9\-]*[a-zA-Z0-9])\.)*([A-Za-z0-9]|[A-Za-z0-9][A-Za-z0-9\-]*[A-Za-z0-9])$"
