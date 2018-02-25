# coding = utf8

import logging, hashlib, xml.sax

logger = logging.getLogger(__name__)


def signature(data, _type='sha1', key=None):
    keys = data.keys()
    keys.sort()
    tmpstr = '&'.join('%s=%s' % (k,data[k]) for k in keys)
    if key:
        tmpstr += '&key=' + key
    logger.debug('signature params string %s %s' % (_type, tmpstr))

    tmpstr = tmpstr
    if _type == 'md5':
        hash_md5 = hashlib.md5(tmpstr.encode('utf-8'))
        sign = hash_md5.hexdigest()
    else:
        hash_sha1 = hashlib.sha1(tmpstr)
        sign = hash_sha1.hexdigest()

    logger.debug('signature %s %s' % (_type, sign))
    return sign


def parsexml(xmlstring):
    class XMLHandler(xml.sax.handler.ContentHandler):
        def __init__(self):
            self.buffer = ""
            self.mapping = {}

        def startElement(self, name, attributes):
            self.buffer = ""

        def characters(self, data):
            self.buffer += data

        def endElement(self, name):
            self.mapping[name] = self.buffer

        def getDict(self):
            return self.mapping

    try:
        xmlh = XMLHandler()
        xml.sax.parseString(xmlstring, xmlh)
        return xmlh.getDict()
    except:
        logger.error('parse xmlstring(%s) failed' % xmlstring)
        return