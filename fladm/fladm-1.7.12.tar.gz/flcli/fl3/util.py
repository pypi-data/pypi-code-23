import requests


def build_headers(raw):
    headers = {}

    for line in raw.split('\n'):
        line = line.strip()
        if len(line) > 0:
            t = line.lstrip().split(':')
            headers[t[0]] = ':'.join(t[1:]).lstrip()

    return headers


def get_filename(filename):
    return filename.split('/')[-1]


def fetch_post(url, data, headers):
    r = requests.post(url, data=data, headers=headers)
    # print '\nurl=%s\n%s' % (url, r.content)
    # pprint.pprint(headers)
    return r
