from pbraw import dispatcher
from pbraw.util import urlparse, urlunparse, get_url
from pbraw.handlers.plain import grab_plain

def modifier(selector, decoder, transformer, encoder, string):
    def f(x):
        a = x[:]
        a[selector] = encoder(transformer(decoder(a[selector]), string))
        return urlunparse(a)
    return f

split_path = lambda x: x.split('/')[1:]
join_path = lambda x: '/' + '/'.join(x)

p_prepender = lambda label: modifier(2, split_path, lambda x, y: [y] + x, join_path, label)
p_appender = lambda label: modifier(2, split_path, lambda x, y: x + [y], join_path, label)
p_replacer = lambda label: modifier(2, split_path, lambda x, y: [y] + x[1:], join_path, label)
p_inserter = lambda label: modifier(2, split_path,
        lambda x, y: x[0:1] + [y] + x[1:],
        join_path, label)
q_prepender = lambda label: modifier(4,
        lambda x: [tuple(y.split('=')) for y in x.split('&')],
        lambda x, y: list(filter(lambda z: z[0] != y, x)) + [(y, '1')],
        lambda x: '&'.join(['='.join(y) for y in x]),
        label)

@dispatcher.handler(priority=10)
def grab_rewriting_urls(url, req):
    if not req.headers['content-type'].startswith('text/html'):
        return False
    purl = list(urlparse(url))
    links = set()
    for label in ['raw', 'download', 'plain', 'dl']:
        links.update([f(label)(purl) for f in [p_prepender, p_appender, p_replacer, p_inserter, q_prepender]])

    #res = []
    for link in links:
        r = get_url(link)
        if not r:
            continue
        ret = grab_plain(link, r)
        if ret:
            return ret
            #res.extend(ret)
            #break
    #return res if res else False
    return False
