import requests
import urlparse 
import os
import sys
import logging

from okerrclient.exceptions import OkerrExc


class okerrclient_api():
    def __init__(self):
        self.base_url = 'https://cp.okerr.com/'
        self.api_url = None
        self.log = self.openlog()
        self.api_user = None
        self.api_pass = None
        
    # add API arguments to parser
    def make_parser(self, parser):
        parser_apir = parser.add_argument_group('API commands (reading)')
        parser_apir.add_argument('--api-director', default=None, const='', nargs='?', help='get server for project')
        parser_apir.add_argument('--api-indicator', action='store_true', help='get JSON for 1 indicator')
        parser_apir.add_argument('--api-indicators', metavar='prefix', default=None, const='', nargs='?', help='list indicators by prefix')
        parser_apir.add_argument('--api-tags', metavar='tags', default=None, nargs='+', help='tags (for tagfilter)')
        parser_apir.add_argument('--api-notags', metavar='tags', default=None, nargs='+', help='tags (for tagfilter) for negative filtering')
        parser_apir.add_argument('--api-getarg', metavar='argument', default=None, help='get one argument of indicator')
        parser_apir.add_argument('--api-checkmethods', action='store_true', help='show checkmethods information')



        
        parser_apiw = parser.add_argument_group('API commands (writing)')
        parser_apiw.add_argument('--api-create', action='store_true', help='create indicator by name (with default checkmethod, all options and arguments)')
        parser_apiw.add_argument('--api-delete', action='store_true', help='delete indicator by name')
        parser_apiw.add_argument('--api-setarg', nargs='+', metavar="argname=value", help='set indicator arguments (name=value)')
        parser_apiw.add_argument('--api-set', nargs='+', metavar="option=value", help='set indicator options (name=value)')


        parser_apiw = parser.add_argument_group('Partner API commands')
        parser_apiw.add_argument('--partner-create', metavar=('partner_id', 'email'), nargs=2, help='create user')
        parser_apiw.add_argument('--partner-check', metavar='partner_id', help='check user info')
        parser_apiw.add_argument('--partner-list', default=False, action='store_true', help='list all users')
        parser_apiw.add_argument('--partner-grant', metavar=('partner_id', 'group'), nargs=2, help='grant user group')
        parser_apiw.add_argument('--partner-grant-new', metavar=('partner_id', 'group'), nargs=2, help='grant user new group')
        parser_apiw.add_argument('--partner-revoke', metavar=('partner_id', 'group', 'expiration'), nargs=3, help='revoke user from group')


        parser_apio = parser.add_argument_group('API options')
        parser_apio.add_argument('--api-url',  help='specify API URL (optional!)')
        parser_apio.add_argument('--api-user', help='okerr username')
        parser_apio.add_argument('--api-pass', help='okerr password')


    def director(self, name=None):
        if name is None:
            name = self.textid
        
        if self.api_user and self.api_pass:
            auth = (self.api_user, self.api_pass)
        else:
            auth=None
            
        url = urlparse.urljoin(self.base_url, '/api/director/{}'.format(name))
        self.log.debug(u'getting project url from {}'.format(url))
        r = requests.get(url, auth=auth)
        self.log.debug(u'status code: {}'.format(r.status_code))
        return r.text.strip()

    def set_api_url(self,name=None):
        
        if self.api_url:
            self.log.debug("set_api_url already have url: {}".format(self.api_url))
            return
        
        self.api_url = self.director(name)


        
    def openlog(args,name='APILogger'):
        log = logging.getLogger(name)
                
        err = logging.StreamHandler(sys.stderr)
        log.addHandler(err)

        #log.setLevel(logging.INFO)

        return log

    def verbose(self):
        self.log.setLevel(logging.DEBUG)


    # main functions
    
    def indicators(self, prefix):
    
        self.set_api_url()
        
        url = urlparse.urljoin(self.api_url, u'/api/indicators/{}/{}'.format(self.textid, prefix))
        self.log.debug(u'getting indicators list from url {}'.format(url))

        auth = (self.api_user, self.api_pass)
        r = requests.get(url, auth=auth)
        self.log.debug(u'status code: {}'.format(r.status_code))
        if r.status_code != 200:
            self.log.error(r.text)
            return

        print r.text.strip().encode('utf-8')

    def indicator(self, iname):

        self.set_api_url()

        url = urlparse.urljoin(self.api_url, u'/api/indicator/{}/{}'.format(self.textid, iname))
        self.log.debug(u'getting indicator from url {}'.format(url))
        auth = (self.api_user, self.api_pass)
        r = requests.get(url, auth=auth)
        self.log.debug(u'status code: {}'.format(r.status_code))
        if r.status_code != 200:
            self.log.error(r.text)
            raise OkerrExc(r.text)
            return

        print r.text.strip().encode('utf-8')

    
    def partner_create(self, partner_id, email):
        data = {
            'email': email,
            'partner_id': partner_id,
        }

        # self.set_api_url(email)

        url = urlparse.urljoin(self.base_url, u'/api/partner/create')
        self.log.debug(u'create user. email {} partner_id: {}'.format(email, partner_id))
        auth = (self.api_user, self.api_pass)
        r = requests.post(url, auth=auth, data=data)
        self.log.debug(u'status code: {}'.format(r.status_code))
        if r.status_code != 200:
            self.log.error(r.text)
            return

        print r.text.strip().encode('utf-8')

    def partner_check(self, partner_id):

        self.set_api_url(u'p:{}'.format(partner_id))

        url = urlparse.urljoin(self.api_url, u'/api/partner/check/{}'.format(partner_id))
        self.log.debug(u'check user. partner_id: {}'.format(partner_id))
        auth = (self.api_user, self.api_pass)
        r = requests.get(url, auth=auth)
        self.log.debug(u'status code: {}'.format(r.status_code))
        if r.status_code != 200:
            self.log.error(r.text)
            return

        print r.text.strip().encode('utf-8')

    def partner_grant(self, partner_id, group, new=False):

        self.set_api_url(u'p:{}'.format(partner_id))

        data = {
            'group': group,
            'partner_id': partner_id,
            'new': 0
        }
        
        if new:
            data['new']=1

        url = urlparse.urljoin(self.api_url, u'/api/partner/grant')
        self.log.debug(u'grant group {} to user partner_id: {} url: {}'.format(group, partner_id, url))
        auth = (self.api_user, self.api_pass)
        r = requests.post(url, auth=auth, data=data)
        self.log.debug(u'status code: {}'.format(r.status_code))
        if r.status_code != 200:
            self.log.error(r.text)
            return

        print r.text.strip().encode('utf-8')

    def partner_revoke(self, partner_id, group, expiration):

        data = {
            'group': group,
            'partner_id': partner_id,
            'exp': expiration
        }

        self.set_api_url('p:{}'.format(partner_id))

        url = urlparse.urljoin(self.api_url, u'/api/partner/revoke')
        self.log.debug(u'revoke group {} (exp: {}) from partner_id: {}'.format(group, expiration, partner_id))
        auth = (self.api_user, self.api_pass)
        r = requests.post(url, auth=auth, data=data)
        self.log.debug(u'status code: {}'.format(r.status_code))
        if r.status_code != 200:
            self.log.error(r.text)
            return

        print r.text.strip().encode('utf-8')




    def partner_list(self):

        url = urlparse.urljoin(self.base_url, u'/api/partner/list')
        self.log.debug(u'partner/list users, url: {}'.format(url))
        auth = (self.api_user, self.api_pass)
        r = requests.get(url, auth=auth)
        self.log.debug(u'status code: {}'.format(r.status_code))
        if r.status_code != 200:
            self.log.error(r.text)
            return

        print r.text.strip().encode('utf-8')



    def create(self, iname):

        self.set_api_url()

        url = urlparse.urljoin(self.api_url, u'/api/create/{}/{}'.format(self.textid, iname))
        self.log.debug(u'create indicator. url {}'.format(url))
        auth = (self.api_user, self.api_pass)
        r = requests.post(url, auth=auth)
        self.log.debug(u'status code: {}'.format(r.status_code))
        if r.status_code != 200:
            self.log.error(r.text)
            return

        print r.text.strip().encode('utf-8')


    def delete(self, iname):

        self.set_api_url()

        url = urlparse.urljoin(self.api_url, u'/api/delete/{}/{}'.format(self.textid, iname))
        self.log.debug(u'delete indicator. url {}'.format(url))
        auth = (self.api_user, self.api_pass)
        r = requests.post(url, auth=auth)
        self.log.debug(u'status code: {}'.format(r.status_code))
        if r.status_code != 200:
            self.log.error(r.text)
            return

        print r.text.strip().encode('utf-8')

    def setarg(self, iname, args):

        data=dict()
        for arg in args:
            (k,v) = arg.split('=')
            data[k]=v

        self.set_api_url()

        url = urlparse.urljoin(self.api_url, u'/api/setarg/{}/{}'.format(self.textid, iname))
        self.log.debug(u'set args for indicator. url {}'.format(url))
        auth = (self.api_user, self.api_pass)
        r = requests.post(url, auth=auth, data=data)
        self.log.debug(u'status code: {}'.format(r.status_code))
        if r.status_code != 200:
            self.log.error(r.text)
            return

        print r.text.strip().encode('utf-8')


    def set(self, iname, args):

        data=dict()
        for arg in args:
            (k,v) = arg.split('=')
            data[k]=v

        self.set_api_url()

        url = urlparse.urljoin(self.api_url, u'/api/set/{}/{}'.format(self.textid, iname))
        self.log.debug(u'set options for indicator. url {}'.format(url))
        auth = (self.api_user, self.api_pass)
        r = requests.post(url, auth=auth, data=data)
        self.log.debug(u'status code: {}'.format(r.status_code))
        if r.status_code != 200:
            self.log.error(r.text)
            return

        print r.text.strip().encode('utf-8')


    def getarg(self, iname, argname):

        self.set_api_url()

        url = urlparse.urljoin(self.api_url, u'/api/getarg/{}/{}/{}'.format(self.textid, iname,argname))
        self.log.debug(u'getting argument from url {}'.format(url))
        auth = (self.api_user, self.api_pass)
        r = requests.get(url, auth=auth)
        self.log.debug(u'status code: {}'.format(r.status_code))
        if r.status_code != 200:
            self.log.error(r.text)
            return

        print r.text.strip().encode('utf-8')


    def checkmethods(self):

        self.set_api_url()

        url = urlparse.urljoin(self.api_url, u'/api/checkmethods')
        self.log.debug(u'getting checkmethods from url {}'.format(url))
        r = requests.get(url) # NOAUTH 
        self.log.debug(u'status code: {}'.format(r.status_code))
        if r.status_code != 200:
            self.log.error(r.text)
            return

        print r.text.strip().encode('utf-8')



    def tagfilter(self, tags, notags):

        taglist = list()

        if tags:
            for tag in tags:
                taglist.append(tag)

        if notags:
            for tag in notags:
                taglist.append('-'+tag)

        self.log.debug("taglist: {}".format(taglist))

        self.set_api_url()

        url = urlparse.urljoin(self.api_url, u'/api/tagfilter/{}/'.format(self.textid))
        self.log.debug(u'url: {}'.format(url))

        for tag in taglist:            
            url = urlparse.urljoin(url, unicode(tag)+'/')

        self.log.debug(u'getting tag filter from url {}'.format(url))
        auth = (self.api_user, self.api_pass)
        r = requests.get(url, auth=auth)
        self.log.debug(u'status code: {}'.format(r.status_code))
        if r.status_code != 200:
            self.log.error(r.text)
            return

        print r.text.strip().encode('utf-8')


    # handler

    def run_api_commands(self, args):

        worked = False

        # take options from environment
        if 'OKERR_API_USER' in os.environ:
            self.api_user = os.environ['OKERR_API_USER']
        if 'OKERR_API_PASS' in os.environ:
            self.api_pass = os.environ['OKERR_API_PASS']
        if 'OKERR_API_URL' in os.environ:
            self.api_url = os.environ['OKERR_API_URL']

        # take options from CLI
        if args.defname:
            self.iname = unicode(args.defname, 'utf-8')
        if args.url:
            self.base_url = unicode(args.url, 'utf-8')
        if args.textid:
            self.textid = args.textid
        if args.api_user:
            self.api_user = args.api_user
        if args.api_pass:
            self.api_pass = args.api_pass            
        if args.api_url:
            self.api_url = unicode(args.api_url, 'utf-8')            

        if args.verbose:
            self.verbose()


        if args.partner_create:
            self.partner_create(args.partner_create[0], args.partner_create[1])
            worked = True
        
        if args.partner_check:
            self.partner_check(args.partner_check)
            worked = True

        if args.partner_list:
            self.partner_list()
            worked = True

        if args.partner_grant:
            self.partner_grant(args.partner_grant[0], args.partner_grant[1])
            worked = True

        if args.partner_grant_new:
            self.partner_grant(args.partner_grant_new[0], args.partner_grant_new[1], new=True)
            worked = True

        if args.partner_revoke:
            self.partner_revoke(args.partner_revoke[0], args.partner_revoke[1], args.partner_revoke[2])
            worked = True

        if args.api_create:
            self.create(self.iname)
            worked = True
        
        if args.api_director is not None:
            if args.api_director:
                name = args.api_director
            else:
                # not specified, use textid
                name = self.textid
            print self.director(name)        
            worked = True
        
        if args.api_indicator:
            self.indicator(self.iname)    
            worked = True

        if args.api_indicators is not None:
            self.indicators(unicode(args.api_indicators, 'utf-8'))    
            worked = True
        
        if args.api_tags or args.api_notags:
            self.tagfilter(args.api_tags, args.api_notags)
            worked = True

        if args.api_getarg:
            self.getarg(self.iname, args.api_getarg)
            worked = True

        if args.api_checkmethods:
            self.checkmethods()
            worked = True


        if args.api_set:
            self.set(self.iname, args.api_set)
            worked = True

        if args.api_setarg:
            self.setarg(self.iname, args.api_setarg)
            worked = True

        if args.api_delete:
            self.delete(self.iname)
            worked = True

        return worked
        
