import string

default_url_root = "http://www.icefilms.info/"
abc_keys = list("1" + string.ascii_uppercase)
tvshow_id_regex = r"\A\d+/\d+\Z"

_sentinel = object()
def _getfirst (url, name, default=_sentinel):
    from urllib.parse import urlsplit, parse_qs
    ls = parse_qs(urlsplit(url).query).get(name, [])
    if default is not _sentinel:
        ls.append(default)
    return ls[0]

def _get_video_info_href (video_id):
    return (
        "membersonly/"
        "components/"
        "com_iceplayer/"
        "video.php?h=374&w=631&vid={video_id}&img="
    ).format(**locals())

def _get_video_source_info_href (video_id, source_id):
    return (
        "membersonly/"
        "components/"
        "com_iceplayer/"
        "video.phpAjaxResp.php"
        "?s={source_id}&t={video_id}"
    ).format(**locals())

def _label_get_title_year (label):
    import re
    m = re.search(r"\A(.*)\s+\((\d+)\)\Z", label)
    if m:
        return m.group(1), int(m.group(2))
    else:
        return label.strip(), None

def _soup_iter_programs (soup):
    for a in soup.find(class_="list").find_all("a", href=True):
        title, year = _label_get_title_year(a.text)
        yield title, year, a["href"]

def _label_extract_episode (label):
    import re
    m = re.search(r"\A(\d+)x(\d+)\s+(.*)\s*\Z", label)
    if m:
        season_num, num, title = m.groups()
        return title, int(season_num), int(num)
    else:
        return None, None, label

class WebGapColdfilms:
    def __init__ (self, webgap, url_root=default_url_root):
        self._webgap = webgap
        self._url_root = url_root
        self._cookies = dict()

    ############################################################
    # Private methods
    ############################################################

    def _make_request (self, href, method="GET", headers={}, body=None, use_cookies=False, set_cookies=False):
        from urllib.parse import urljoin
        url = urljoin(self._url_root, href)
        headers = dict(headers)
        headers.setdefault("User-Agent", " ".join([
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_3)",
            "AppleWebKit/537.36 (KHTML, like Gecko)",
            "Chrome/60.0.3112.90",
            "Safari/537.36",
        ]))
        headers.setdefault("Accept", "*/*")
        if use_cookies:
            headers.setdefault("Cookie", "; ".join(k+"="+v for k,v in self._cookies.items()))

        response = self._webgap.call(url, method=method, headers=headers, body=body)._orig_response
        if set_cookies:
            self._cookies = dict(response.cookies)
        response.raise_for_status()
        return response

    def _make_soup (self, *args, **kwargs):
        import bs4
        return bs4.BeautifulSoup(self._make_request(*args, **kwargs).text, "html5lib")

    ############################################################
    # Public API
    ############################################################

    def iter_movies (self, abc_key):
        import steov
        if abc_key not in abc_keys:
            raise ValueError("abc_key: must be one of: " + "".join(abc_keys))
        soup = self._make_soup("/movies/a-z/" + abc_key)
        for title, year, href in _soup_iter_programs(soup):
            yield steov.Anon(id=int(_getfirst(href, "v")), title=title, year=year)

    def iter_tvshows (self, abc_key):
        import re
        import steov
        from urllib.parse import urlsplit
        if abc_key not in abc_keys:
            raise ValueError("abc_key: must be one of: " + "".join(abc_keys))
        soup = self._make_soup("/tv/a-z/" + abc_key)
        for title, year, href in _soup_iter_programs(soup):
            m = re.search(r"\btv\/series\/(\d+\/\d+)\b", urlsplit(href).path)
            if not m:
                continue
            yield steov.Anon(id=m.group(1), title=title, year=year)

    def get_tvshow (self, id):
        import re
        import steov
        if not re.search(tvshow_id_regex, id):
            error = ValueError("id: must match regex " + tvshow_id_regex)
            error.actual_value = id
            raise error

        soup = self._make_soup("tv/series/" + id)
        tvshow = steov.Anon(id=id, seasons=[])
        season = None
        for elem in soup.find(class_="list").children:
            if elem.name == "h3":
                title, year = _label_get_title_year(list(elem.stripped_strings)[0])
                m = re.search(r"\Aseason\s+(\d+)\Z", title, re.I)
                if m:
                    num = int(m.group(1))
                else:
                    num = None
                season = steov.Anon(title=title, year=year, num=num, episodes=[])
                tvshow.seasons.append(season)
            elif elem.name == "a" and elem.has_attr("href"):
                title, num, season_num = _label_extract_episode(elem.text)
                season.episodes.append(steov.Anon(id=int(_getfirst(elem["href"], "v")), title=title, num=num, season_num=season_num))
        return tvshow

    def get_video (self, id):
        import re
        import steov
        if not isinstance(id, int):
            raise TypeError("id: must be int")
        if id <= 0:
            raise ValueError("id: must be positive")
        soup = self._make_soup(_get_video_info_href(id), set_cookies=True)
        video = steov.Anon(id=id, source_groups=[])
        # TODO parse the soup at the following url for vid info:
        # http://www.icefilms.info/ip.php?v={video_id}&
        source_group = None
        for section_elem in soup(class_="ripdiv"):
            for elem in section_elem.children:
                already = False
                if elem.name == "b":
                    source_group = steov.Anon(title=elem.text, sources=[])
                    video.source_groups.append(source_group)
                    continue
                if elem.a is None:
                    continue
                m = re.search(r"\bgo\((\d+)\)", elem.a["onclick"])
                if not m:
                    continue
                source_group.sources.append(steov.Anon(id=int(m.group(1)), location=elem.a.span.text))
        return video

    def get_video_source_url (self, video_id, source_id):
        from urllib.parse import urlencode, urljoin
        if not isinstance(video_id, int):
            raise TypeError("video_id: must be int")
        if video_id <= 0:
            raise ValueError("video_id: must be positive")
        if not isinstance(source_id, int):
            raise TypeError("source_id: must be int")
        if source_id <= 0:
            raise ValueError("source_id: must be positive")
        return _getfirst(_getfirst(self._make_request(
            _get_video_source_info_href(video_id, source_id),
            method="POST",
            headers={
                "Referer": urljoin(self._url_root, _get_video_info_href(video_id)),
                "Content-Type": "application/x-www-form-urlencoded",
            },
            body=urlencode({
                "id": source_id,
                "t": video_id,
                "s": 10005,
                "m": 10069,
                "iqs": "",
                "url": "",
                "cap": " ",
                "sec": "37fn8Oklq",
            }).encode("ascii"),
            use_cookies=True,
        ).text, "url"), "url")

    def search (self, query):
        import re
        from urllib.parse import quote, urlsplit
        import steov
        soup = self._make_soup(href="search.php?q=" + quote(query))
        weak = False
        for elem in soup.find(class_="SR").find_all(("td", "h3")):
            if elem.name == "h3" and "weak".casefold() in elem.text.casefold():
                weak = True
            elif elem.name == "td":
                a = elem.a
                # TODO extract <b> elements to identify query matches
                result = steov.Anon(title=a.text.strip(), description_part=elem.find(class_="desc").text, weak=weak)
                href = a["href"]
                id_str = _getfirst(href, "v", None)
                if id_str is not None:
                    result.type = "video"
                    result.id = int(id_str)
                else:
                    m = re.search(r"\btv\/series\/(\d+\/\d+)\b", urlsplit(href).path)
                    if m:
                        result.type = "tvshow"
                        result.id = m.group(1)
                    else:
                        # TODO exception? log?
                        continue
                yield result
