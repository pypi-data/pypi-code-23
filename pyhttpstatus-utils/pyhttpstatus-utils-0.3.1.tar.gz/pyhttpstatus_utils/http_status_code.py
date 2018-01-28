#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#  @copyright 2018 TUNE, Inc. (http://www.tune.com)
#  @namespace pyhttpstatus_utils

"""
HTTP Status Codes
"""

class HttpStatusCode(object):
    """HTTP Status Codes
    """

    CONTINUE = 100  # HTTP/1.1, RFC 2616, Section 10.1.1
    SWITCHING_PROTOCOLS = 101  # HTTP/1.1, RFC 2616, Section 10.1.2
    PROCESSING = 102  # WEBDAV, RFC 2518, Section 10.1

    OK = 200  # HTTP/1.1, RFC 2616, Section 10.2.1
    CREATED = 201  # HTTP/1.1, RFC 2616, Section 10.2.2
    ACCEPTED = 202  # HTTP/1.1, RFC 2616, Section 10.2.3
    NON_AUTHORITATIVE_INFORMATION = 203  # HTTP/1.1, RFC 2616, Section 10.2.4
    NO_CONTENT = 204  # HTTP/1.1, RFC 2616, Section 10.2.5
    RESET_CONTENT = 205  # HTTP/1.1, RFC 2616, Section 10.2.6
    PARTIAL_CONTENT = 206  # HTTP/1.1, RFC 2616, Section 10.2.7
    MULTI_STATUS = 207  # WEBDAV RFC 2518, Section 10.2
    ALREADY_REPORTED = 208
    IM_USED = 226  # Delta encoding in HTTP, RFC 3229, Section 10.4.1

    MULTIPLE_CHOICES = 300  # HTTP/1.1, RFC 2616, Section 10.3.1
    MOVED_PERMANENTLY = 301  # HTTP/1.1, RFC 2616, Section 10.3.2
    MOVED_TEMPORARILY = 302  # HTTP/1.1, RFC 2616, Section 10.3.3
    SEE_OTHER = 303  # HTTP/1.1, RFC 2616, Section 10.3.4
    NOT_MODIFIED = 304  # HTTP/1.1, RFC 2616, Section 10.3.5
    USE_PROXY = 305  # HTTP/1.1, RFC 2616, Section 10.3.6
    SWITCH_PROXY = 306  # HTTP/1.1, RFC 2616, Section 10.3.6
    TEMPORARY_REDIRECT = 307  # HTTP/1.1, RFC 2616, Section 10.3.8

    BAD_REQUEST = 400  # HTTP/1.1, RFC 2616, Section 10.4.1
    UNAUTHORIZED = 401  # HTTP/1.1, RFC 2616, Section 10.4.2
    PAYMENT_REQUIRED = 402  # HTTP/1.1, RFC 2616, Section 10.4.3
    FORBIDDEN = 403  # HTTP/1.1, RFC 2616, Section 10.4.4
    NOT_FOUND = 404  # HTTP/1.1, RFC 2616, Section 10.4.5
    METHOD_NOT_ALLOWED = 405  # HTTP/1.1, RFC 2616, Section 10.4.6
    NOT_ACCEPTABLE = 406  # HTTP/1.1, RFC 2616, Section 10.4.7
    PROXY_AUTHENTICATION_REQUIRED = 407  # HTTP/1.1, RFC 2616, Section 10.4.8
    REQUEST_TIMEOUT = 408  # HTTP/1.1, RFC 2616, Section 10.4.9
    CONFLICT = 409  # HTTP/1.1, RFC 2616, Section 10.4.10
    GONE = 410  # HTTP/1.1, RFC 2616, Section 10.4.11
    LENGTH_REQUIRED = 411  # HTTP/1.1, RFC 2616, Section 10.4.12
    PRECONDITION_FAILED = 412  # HTTP/1.1, RFC 2616, Section 10.4.13
    REQUEST_ENTITY_TOO_LARGE = 413  # HTTP/1.1, RFC 2616, Section 10.4.14
    REQUEST_URI_TOO_LONG = 414  # HTTP/1.1, RFC 2616, Section 10.4.15
    UNSUPPORTED_MEDIA_TYPE = 415  # HTTP/1.1, RFC 2616, Section 10.4.16
    REQUESTED_RANGE_NOT_SATISFIABLE = 416  # HTTP/1.1, RFC 2616, Section 10.4.17
    EXPECTATION_FAILED = 417  # HTTP/1.1, RFC 2616, Section 10.4.18
    UNPROCESSABLE_ENTITY = 422  # WEBDAV, RFC 2518, Section 10.3
    LOCKED = 423  # WEBDAV RFC 2518, Section 10.4
    FAILED_DEPENDENCY = 424  # WEBDAV, RFC 2518, Section 10.5
    UPGRADE_REQUIRED = 426  # HTTP Upgrade to TLS, RFC 2817, Section 6
    PRECONDITION_REQUIRED = 428  # [RFC6585]
    TOO_MANY_REQUESTS = 429  # [RFC6585]
    REQUEST_HEADER_FIELDS_TOO_LARGE = 431  # The server is unwilling to
    # process the request because its header fields are too large.

    UNAVAILABLE_FOR_LEGAL_REASONS = 451

    INTERNAL_SERVER_ERROR = 500  # HTTP/1.1, RFC 2616, Section 10.5.1
    NOT_IMPLEMENTED = 501  # HTTP/1.1, RFC 2616, Section 10.5.2
    BAD_GATEWAY = 502  # HTTP/1.1 RFC 2616, Section 10.5.3
    SERVICE_UNAVAILABLE = 503  # HTTP/1.1, RFC 2616, Section 10.5.4
    GATEWAY_TIMEOUT = 504  # HTTP/1.1 RFC 2616, Section 10.5.5
    HTTP_VERSION_NOT_SUPPORTED = 505  # HTTP/1.1, RFC 2616, Section 10.5.6
    VARIANT_ALSO_NEGOTIATES = 506
    INSUFFICIENT_STORAGE = 507  # WEBDAV, RFC 2518, Section 10.6
    LOOP_DETECTED = 508
    BANDWIDTH_LIMIT_EXCEEDED = 509
    NOT_EXTENDED = 510  # An HTTP Extension Framework, RFC 2774, Section 7
    NETWORK_AUTHENTICATION_REQUIRED = 511  # Client needs to authenticate to gain
    # network access.

    NETWORK_READ_TIMEOUT = 598  # HTTP proxies to signal a network read
    # timeout behind the proxy to a client in front of the proxy.
    NETWORK_CONNECT_TIMEOUT = 599  # HTTP proxies to signal a network connect timeout
    # behind the proxy to a client in front of the proxy.
