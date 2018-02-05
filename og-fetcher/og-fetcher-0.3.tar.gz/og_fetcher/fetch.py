from urllib.request import urlopen

from .parse import parse

def fetch(url):
    try:
        response = urlopen(url)
    except Exception as e:
        return {'error': 'URL could not opened: ' + str(e)}
    
    data = response.read()
    html = ''
    try:
        html = data.decode('utf-8')
    except Exception:
        try:
            html = data.decode('iso-8859-15')
        except Exception:
            response.close()
            return {'error': 'Response could not decoded'}
    response.close()
    
    og_datas = parse(html)
    og = {}
    for og_data in og_datas:
        og[og_data['property']] = og_data['content']
    return og
