# -*- coding: utf8 -*-
""" Different functions for general purpose. """

import re
import socket
import binascii
import datetime
import calendar


def gettext(v, context=None):
    from .manage import manager
    f = manager.get_gettext_callback()
    return f(v, context) if callable(f) else v


def remove_leading_slash(path):
    if not path:
        return path
    if not isinstance(path, str):
        return path
    return path if path[0] != '/' else path[1:]


def ensure_leading_slash(path):
    if not path:
        return path
    if not isinstance(path, str):
        return path
    return path if path[0] == '/' else ("/%s" % path)


def remove_trailing_slash(path):
    if not path:
        return path
    if not isinstance(path, str):
        return path
    return path if path[-1] != '/' else path[:-1]


def ensure_trailing_slash(path):
    if not path:
        return path
    if not isinstance(path, str):
        return path
    return path if path[-1] == '/' else ("%s/" % path)


def path_slashed(path):
    return ensure_leading_slash(ensure_trailing_slash(path))


def path_leading_slash(path):
    return ensure_leading_slash(remove_trailing_slash(path))


def path_trailing_slash(path):
    return ensure_trailing_slash(remove_leading_slash(path))


def path_not_slashed(path):
    return remove_trailing_slash(remove_leading_slash(path))


def fit_image(image, **kwargs):
    """ Resizes given image to fit to given parameters: maximal or minimal
    width and/or height. If minimal and maximal values conflicts with
    each other on the given image - the maximal limitations will be taken.
    @image:                 (image object) The original image to resize to;
    @max_width:             (int)(optional) The maximum width of resulting image;
    @max_height:            (int)(optional) The maximum height of resulting image;
    @min_width:             (int)(optional) The minimum width of resulting image;
    @min_height:            (int)(optional) The minimum height of resulting image;
    @returns:               (image object) The new image object. Even if there is no
                            need to resize at all - the copy of original image will
                            be returned.
    """
    from PIL import Image

    max_width = kwargs.get('max_width', None)
    min_width = kwargs.get('min_width', None)
    max_height = kwargs.get('max_height', None)
    min_height = kwargs.get('min_height', None)
    img_width, img_height = image.size
    if not ((max_width and img_width > max_width)
            or (max_height and img_height > max_height)
            or (min_width and img_width < min_width)
            or (min_height and img_height < min_height)):
        return image.copy()
    mult_max_w = float(max_width) / float(img_width) if max_width and img_width > max_width else 1.0
    mult_max_h = float(max_height) / float(img_height) if max_height and img_height > max_height else 1.0
    mult_min_w = float(img_width) / float(min_width) if min_width and img_width < min_width else 1.0
    mult_min_h = float(img_height) / float(min_height) if min_height and img_height < min_height else 1.0
    mult_max = float(min(mult_max_w, mult_max_h))
    mult_min = float(max(mult_min_w, mult_min_h))
    mult = mult_max if mult_max != 1.0 else mult_min
    if mult == 1.0:
        return image.copy()
    r_width = int(float(img_width) * float(mult))
    r_height = int(float(img_height) * float(mult))
    return image.resize([r_width, r_height], Image.BICUBIC)


def image_thumbnail(image, width, height, crop=True, stretch=True):
    """ Prepares and returns a thumbnail of given image. The original
    image not affects.
    @image:                 (image object) The original image;
    @width:                 (int) The width of resulting thumbnail (in pixels);
    @height:                (int) The height of resulting thumbnail (in pixels);
    @crop:                  (bool)(default=True) if set to 'True' - the image will be
                            resized that way to fill entire thumbnail box, even if
                            a part of it will let outside of borders. For example, for
                            portrait oriented image and boxed thumbnail, top and
                            bottom stripes will be cut off; if set to 'False' - the
                            image will be resized that way to fully fit in the given
                            sizes - width and height, and some space may left white
                            spaced;
    @stretch:               (bool)(default=True) if set to 'True' and the size of the
                            original image is smaller, than required size of thumbnail -
                            image will be zoomed. For example, if the original image has
                            size 30x30 pixels and thumbnail is about to be 64x64 pixels
                            size - the image will be zoomed (stretched) from 30x30 to
                            64x64. If set to 'False' and image is smaller than required
                            size of thumbnail - the size of image will not be changed.
    @returns:               (image object) The resulting thumbnail image object.
    """
    from PIL import Image

    img_width, img_height = image.size
    # If size of the original image is the same as required - just
    # return original image
    if img_width == width and img_height == height:
        return image.copy()
    # If size (both width and height) is smaller than required and
    # 'stretch' is not set_value to 'True' - return original image
    if img_width <= width and img_height <= height and not stretch:
        return image.copy()
    # Resizing image to the required sizes
    mult = 1.0
    # If stretch is required
    if (img_width < width or img_height < height) and stretch:
        mult_w = float(width) / float(img_width)
        mult_h = float(height) / float(img_height)
        mult = float(max(mult_w, mult_h))
    r_img_width = int(float(img_width) * float(mult))
    r_img_height = int(float(img_height) * float(mult))
    # If resize is required. Depending on the existing multiplier, which is
    # 1.0 by default (no strech affected) and may be modified by stretch mechanics
    if r_img_width > width or r_img_height > height:
        mult_w = float(width) / float(r_img_width)
        mult_h = float(height) / float(r_img_height)
        mult *= float(min((max(mult_w, mult_h) if crop else min(mult_w, mult_h)), 1.0))
        r_img_width = int(float(img_width) * float(mult))
        r_img_height = int(float(img_height) * float(mult))
    thumbnail = image.resize([r_img_width, r_img_height], Image.BICUBIC)
    img_width, img_height = thumbnail.size
    # If crop is required and the picture is not boxed - do crop
    if crop and (img_width != img_height):
        if img_width > img_height:
            r_top = 0
            r_bottom = img_height - 1
            r_left = (img_width / 2) - (width / 2)
            r_right = (img_width / 2) + (width / 2)
        else:
            r_left = 0
            r_right = 0
            r_top = (img_height / 2) - (height / 2)
            r_bottom = (img_height / 2) + (height / 2)
        thumbnail = thumbnail.crop([r_left, r_top, r_right, r_bottom])
    return thumbnail


def split_search_phrase(phrase):
    """ Splits the search phrase (one solid string of text) into the search words. Words can be
    simple - """
    if not isinstance(phrase, str):
        raise TypeError("'split_findphrase' requires that parameter to be a (str)!")
    if not phrase:
        return []
    r = []
    vv = re.findall(r'[^"\s]\S*|".+?"', phrase.replace('\'', '"').replace('""', '"'))
    for v in vv:
        v_ = re.sub("[!\(\)\-\_\+\=\[\]\{\}\/\"\\\:\;\,\.\?\<\>]", "", v)
        if not v_:
            continue
        r.append(str(v).replace('"', ''))
    return r


def ipaddr_version(val):
    """ Checks the version of IP address, returning numeric 4 for IPv4, numeric 6 for IPv6 or 0 otherwise. """
    if not isinstance(val, str):
        raise TypeError("'ipaddr_version' requires value to be type of (str)!")
    if '.' in val and val.count('.') == 3:
        p = val.split('.')
        if not p[0].isdigit() or not p[1].isdigit() or not p[2].isdigit() or not p[3].isdigit():
            return 0
        if int(p[0]) > 255 or int(p[1]) > 255 or int(p[2]) > 255 or int(p[3]) > 255:
            return 0
        return 4
    elif ':' in val and val.count('::') <= 1:
        p = val.split(':')
        if len(p) > 8:
            return 0
        for p_ in p:
            if p_ == "":
                continue
            if len(p_) > 4:
                return 0
            if re.sub("[^0-9a-fA-F]", "", str(p_)) != p_:
                return 0
        return 6
    else:
        return 0


def hex2ip(val):
    """ Converts heximal IP address to the corresponding textual format. Returns 'None'
    string if incorrect value given. """
    try:
        val = str(val)
        if len(val) == 8:
            return socket.inet_ntop(socket.AF_INET, binascii.unhexlify(val))
        elif len(val) == 32:
            return socket.inet_ntop(socket.AF_INET6, binascii.unhexlify(val))
        else:
            return None
    except (binascii.Error, OSError):
        return None


def ip2hex(val):
    """ Converts textual IP address (IPv4 or IPv6) to the heximal string. Returns
    'None' if invalid address or empty value given. """
    if not val:
        return None
    ipvers = ipaddr_version(val)
    try:
        if ipvers == 0:
            return None
        elif ipvers == 4:
            return binascii.hexlify(socket.inet_pton(socket.AF_INET, val)).upper()
        elif ipvers == 6:
            return binascii.hexlify(socket.inet_pton(socket.AF_INET6, val)).upper()
        else:
            return None
    except (binascii.Error, OSError):
        return None


def int_2_ipv4(val):
    """ Converts integer value to the textual IPv4 address. Not working with IPv6, use
    heximal values instead. """
    val = int(val)
    o1 = int(val / 16777216) % 256
    o2 = int(val / 65536) % 256
    o3 = int(val / 256) % 256
    o4 = val % 256
    return "%i.%i.%i.%i" % (o1, o2, o3, o4)


def ipv4_2_int(val):
    """ Converts textual IPv4 to integer. Not working with IPv6, use heximal instead. """
    if ipaddr_version(val) != 4:
        return None
    return int(ip2hex(val), 16)


def int2mac(val, separator='.'):
    """ Converts integer to textual network L2 MAC address. """
    mac_ = "%0.12x" % val
    if not separator:
        return mac_
    elif separator == '.':
        return "%s.%s.%s" % (str(mac_[0:4]), str(mac_[4:8]), str(mac_[8:12]))
    else:
        return separator.join([
            mac_[0:2],
            mac_[2:4],
            mac_[4:6],
            mac_[6:8],
            mac_[8:10],
            mac_[10:12]
        ])


def ipv4mask_2_cidr(netmask):
    """ Converts a.b.c.d netmask to the /CIDR format.
    For example: 255.255.255.0 will be converted to the /24 (returned as integer 24). """
    return sum([bin(int(x)).count('1') for x in netmask.split('.')])


def format_datetime(value, format_):
    if not isinstance(format_, str):
        raise TypeError("'format' must be a (str) type!")
    elif not format_:
        raise ValueError("'format' must be set and not be an empty string!")
    v_day = getattr(value, 'day', None)
    v_month = getattr(value, 'month', None)
    v_year = getattr(value, 'year', None)
    v_hours = getattr(value, 'hour', None)
    v_minutes = getattr(value, 'minute', None)
    v_seconds = getattr(value, 'second', None)
    v_weekday = value.isoweekday() if hasattr(value, 'isoweekday') else None
    b_date = bool(v_day is not None and v_month is not None and v_year is not None)
    b_time = bool(v_hours is not None and v_minutes is not None and v_seconds is not None)

    f = dict()
    # %d :: 2-digits day [01..31]
    f['d'] = "%02i" % int(v_day) if b_date else "00"
    # %D :: 3-symbols day of week representation [Mon..Sun]
    if not b_date:
        f['D'] = ""
    else:
        t_weekdays3 = [
            gettext('Mon'),
            gettext('Tue'),
            gettext('Wed'),
            gettext('Thu'),
            gettext('Fri'),
            gettext('Sat'),
            gettext('Sun')
        ]
        f['D'] = t_weekdays3[v_weekday - 1]
    # %j :: day without leading zero [1..31]
    f['j'] = str(v_day) if b_date else "0"
    # %l :: fully named way of week (lowercase L) [Monday..Sunday]
    if not b_date:
        f['l'] = ""
    else:
        t_weekdays = [
            gettext('Monday'),
            gettext('Tuesday'),
            gettext('Wednesday'),
            gettext('Thursday'),
            gettext('Friday'),
            gettext('Saturday'),
            gettext('Sunday')
        ]
        f['l'] = t_weekdays[v_weekday-1]
    # %N :: number of day of week in ISO format [1..7]
    f['N'] = str(v_weekday-1) if b_date else ""
    # %z :: serial number of day of year, starting from zero [0..365]
    if not b_date:
        f['z'] = "0"
    elif isinstance(value, datetime.date) and not isinstance(value, datetime.datetime):
        f['z'] = str((value - datetime.date(value.year, 1, 1)).days)
    else:
        f['z'] = str((value - datetime.datetime(value.year, 1, 1)).days)
    # %W :: serial number of week of year, starting from one [1..]
    f['W'] = "0" if not b_date else str(value.isocalendar()[1])
    # %F :: fully named month, [January..December]
    if not b_date:
        f['F'] = ""
    else:
        t_months = [
            gettext('January'),
            gettext('February'),
            gettext('March'),
            gettext('April'),
            gettext('May'),
            gettext('June'),
            gettext('July'),
            gettext('August'),
            gettext('September'),
            gettext('October'),
            gettext('November'),
            gettext('December')
        ]
        f['F'] = t_months[v_month - 1]
    # %m :: Month with leading zero [01..12]
    f['m'] = "%02i" % int(v_month) if b_date else "00"
    # %M :: 3-symbols name of month [Jan..Dec]
    if not b_date:
        f['M'] = ""
    else:
        t_months3 = [
            gettext('Jan'),
            gettext('Feb'),
            gettext('Mar'),
            gettext('Apr'),
            gettext('May'),
            gettext('Jun'),
            gettext('Jul'),
            gettext('Aug'),
            gettext('Sep'),
            gettext('Oct'),
            gettext('Nov'),
            gettext('Dec')
        ]
        f['M'] = t_months3[v_month - 1]
    # %n :: Month without leading zero [1..12]
    f['n'] = str(v_month) if b_date else "0"
    # %t :: Quantity of days in month [..31]
    f['t'] = str(calendar.monthrange(v_year, v_month)) if b_date else '0'
    # %Y :: 4-digits year
    f['Y'] = str(v_year) if b_date else "0000"
    # %y :: 2-digits year
    f['y'] = str(v_year)[2:] if b_date else "00"
    # %a :: am/pm
    f['a'] = "" if not b_time else ("am" if v_hours < 12 else "pm")
    # %A :: AM/PM
    f['A'] = "" if not b_time else ("AM" if v_hours < 12 else "PM")
    # %g :: hours in 12-hours format without leading zero
    f['g'] = "0" if not b_time else str(12 if v_hours == 0 else (v_hours if v_hours < 12 else (v_hours - 12)))
    # %G :: hours in 24-hours format without leading zero
    f['G'] = "0" if not b_time else str(v_hours)
    # %h :: hours in 12-hours format with leading zero
    f['h'] = "00" if not b_time else "%02i" % int(12 if v_hours == 0 else (v_hours if v_hours < 12 else (v_hours - 12)))
    # %H :: hours in 24-hours format with leading zero
    f['H'] = "00" if not b_time else "%02i" % int(v_hours)
    # %i :: minutes with leading zero [00..59]
    f['i'] = "00" if not b_time else "%02i" % int(v_minutes)
    # %s :: seconds with leading zero [00..59]
    f['s'] = "00" if not b_time else "%02i" % int(v_seconds)

    formatted = format_
    for k in f:
        v = f[k]
        if v is None:
            continue
        k_ = "%" + str(k)
        formatted = formatted.replace(k_, v)

    return formatted


def _str2datetime(value, hasdate, hastime):
    ps = value.split(' ')
    d_ = False
    t_ = False
    n_year = 0
    n_month = 0
    n_day = 0
    n_hour = 0
    n_minute = 0
    n_second = 0
    for p in ps:
        if not p:
            continue
        if '.' not in p and '/' not in p and '\\' not in p and '-' not in p and ':' not in p:
            raise ValueError("Invalid (str) datetime format!")
        if ':' in p:
            if t_:
                raise ValueError("Invalid (str) datetime format!")
            if p.count(':') > 2:
                raise ValueError("Invalid (str) datetime format!")
            p_ = p.split(':')
            if not p_[0].isdigit() or not p_[1].isdigit() or (len(p_) == 3 and not p_[2].isdigit()):
                raise ValueError("Invalid (str) datetime format!")
            n_hour = int(p_[0])
            n_minute = int(p_[1])
            n_second = int(p_[2]) if len(p) == 3 else 0
            if n_hour > 23 or n_minute > 59 or n_second > 59:
                raise ValueError("Invalid (str) datetime format!")
            t_ = True
        else:
            if d_:
                raise ValueError("Invalid (str) datetime format!")
            s = '.' if '.' in p else ('-' if '-' in p else ('/' if '/' in p else '\\'))
            p_ = p.split(s)
            if len(p_) != 3:
                raise ValueError("Invalid (str) datetime format!")
            if not p_[0].isdigit() or not p_[1].isdigit() or not p_[2].isdigit():
                raise ValueError("Invalid (str) datetime format!")
            p1 = int(p_[0])
            p2 = int(p_[1])
            p3 = int(p_[2])
            starting_with_year = p1 > 31 or s == '-'
            if starting_with_year:
                n_year = p1
                if s in ('.', '-'):
                    n_month = p2
                    n_day = p3
                else:
                    n_month = p3
                    n_day = p2
            else:
                n_year = p3
                if s in ('.', '-'):
                    n_month = p2
                    n_day = p1
                else:
                    n_month = p1
                    n_day = p2
            if 99 < n_year < 1000:
                raise ValueError("Invalid (str) datetime format!")
            if n_year < 1000:
                n_year = n_year + 1000 if n_year > 69 else n_year + 2000
            if n_day == 0 or n_month == 0 or n_day > 31 or n_month > 12:
                raise ValueError("Invalid (str) datetime format!")
            n_daysmax = calendar.monthrange(n_year, n_month)[1]
            if n_day > n_daysmax:
                raise ValueError("Invalid (str) datetime format!")
            d_ = True
    if hasdate and not hastime:
        if not d_:
            raise ValueError("Invalid (str) datetime format!")
        value = datetime.date(n_year, n_month, n_day)
    elif not hasdate and hastime:
        if not t_:
            raise ValueError("Invalid (str) datetime format!")
        value = datetime.time(n_hour, n_minute, n_second)
    else:
        if not d_:
            raise ValueError("Invalid (str) datetime format!")
        value = datetime.datetime(n_year, n_month, n_day, n_hour, n_minute, n_second)
    return value


def str2datetime(value):
    return _str2datetime(value, True, True)


def str2date(value):
    return _str2datetime(value, True, False)


def str2time(value):
    return _str2datetime(value, False, True)

