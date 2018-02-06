import json, urllib2
print json.load(urllib2.urlopen('https://www.howsmyssl.com/a/check'))['tls_version']

