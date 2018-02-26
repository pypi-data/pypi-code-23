import webapp2

from im_futuretest import get_test_by_name, get_tests, get_testrun_by_id,\
    get_testruns, run_test, cancel_test_run, delete_test_run,\
    get_json_testrun_by_id, get_web_file_as_string
import json
import logging
import mimetypes
from google.appengine.ext import ndb

_base_route = "futuretest"

def _create_route(suffix):
    global _base_route
    return "/%s/%s" % (_base_route, suffix)

def set_base_route(base_route):
    global _base_route
    _base_route = base_route

def addroutes_futuretest_webapp2(routes):
    routes.extend([
        (_create_route("ui/"), WebRootHandler),
        (_create_route("ui/static/(.*)"), WebStaticHandler),
        (_create_route("tests"), TestsAPIHandler),
        (_create_route("future"), FutureAPIHandler),
        (_create_route("runs"), TestRunsAPIHandler)
    ])
    
class WebRootHandler(webapp2.RequestHandler):
    def get(self):
        lcontent_type = "text/html"
        lcontent = get_web_file_as_string("spa.html")
        self.response.headers.add("Content-Type", lcontent_type)
        self.response.out.write(lcontent)

class WebStaticHandler(webapp2.RequestHandler):
    def get(self, fname):
        lcontent_type = mimetypes.guess_type(fname) or "application/text"
        if isinstance(lcontent_type, tuple):
            lcontent_type = lcontent_type[0]
        logging.info("CT %s: %s" % (fname, {"ct": lcontent_type}))
        lcontent = get_web_file_as_string(fname)
        self.response.headers.add("Content-Type", lcontent_type)
        self.response.out.write(lcontent)

class TestsAPIHandler(webapp2.RequestHandler):
    def get(self):
        ltestname = self.request.get('name')
        ltagsRaw = self.request.get('tags')

        retval = None
        if ltestname:
            retval = get_test_by_name(ltestname.strip())
        else:
            ltags = json.loads(ltagsRaw) if ltagsRaw else []
            retval = get_tests(ltags)
            
        logging.info(retval)
        self.response.headers.add("Content-Type", "application/json")
        self.response.out.write(json.dumps(retval, indent=2))
        
    def post(self):
        lcontentTypeHeader = self.request.headers.get("Content-Type")
        lisJson = lcontentTypeHeader and lcontentTypeHeader.find("application/json") >= 0
        if not lisJson:
            logging.info(self.request.headers.get("Content-Type"))
            self.response.status = 400
            self.response.out.write("json required")
            return

        lbody = json.loads(self.request.body)            
        laction = lbody.get("action")
        if laction == "go":
            ltestname = lbody.get("name")
            if not ltestname:
                self.response.status = 400
                self.response.out.write("name field required")
                return
            else:
                ltest = get_test_by_name(ltestname)
                if not ltest:
                    self.response.status = 404
                    self.response.out.write("can't find test %s" % ltestname)
                    return
                else:
                    ltestRun = run_test(ltestname)
                    retval = {
                        "id": ltestRun.key.id()
                    }
                    self.response.headers.add("Content-Type", "application/json")
                    self.response.out.write(json.dumps(retval, indent=2))
                    return
        else:
            self.response.status = 400
            self.response.out.write("unknown action %s" % laction)
            return

class TestRunsAPIHandler(webapp2.RequestHandler):
    def get(self):
        lid = self.request.get('id')
        ltestname = self.request.get('name')
        lstatuses = self.request.get('statuses')
        lcursorWS = self.request.get("cursor")

        retval = None
        if lid:
            retval = get_json_testrun_by_id(lid)
            if not retval:
                self.response.status = 404
                self.response.out.write("can't find test run for id %s" % lid)
                return
        else:
            retval = get_testruns(ltestname, lstatuses, lcursorWS)
            
        logging.info(retval)
        self.response.headers.add("Content-Type", "application/json")
        self.response.out.write(json.dumps(retval, indent=2))

    def post(self):
        lcontentTypeHeader = self.request.headers.get("Content-Type")
        lisJson = lcontentTypeHeader and lcontentTypeHeader.find("application/json") >= 0
        if not lisJson:
            logging.info(self.request.headers.get("Content-Type"))
            self.response.status = 400
            self.response.out.write("json required")
            return

        lbody = json.loads(self.request.body)            
        laction = lbody.get("action")

        if laction == "cancel":
            lid = lbody.get("id")
            if not lid:
                self.response.status = 400
                self.response.out.write("id field required")
                return
            else:
                ltestRun = get_testrun_by_id(lid)
                
                if not ltestRun:
                    self.response.status = 404
                    self.response.out.write("can't find test run for id %s" % lid)
                    return
                else:
                    cancel_test_run(ltestRun)
                    self.response.out.write("ok")
                    return
        elif laction == "delete":
            lid = lbody.get("id")
            if not lid:
                self.response.status = 400
                self.response.out.write("id field required")
                return
            else:
                ltestRun = get_testrun_by_id(lid)
                
                if not ltestRun:
                    self.response.status = 404
                    self.response.out.write("can't find test run for id %s" % lid)
                    return
                else:
                    delete_test_run(ltestRun)
                    self.response.out.write("ok")
                    return
        else:
            self.response.status = 400
            self.response.out.write("unknown action %s" % laction)
            return

class FutureAPIHandler(webapp2.RequestHandler):
    def get(self):
        lfutureKeyUrlSafe = self.request.get('futurekey')
        lincludeChildren = self.request.get('include_children')
    
        logging.info("lfutureKeyUrlSafe=%s" % lfutureKeyUrlSafe)
        logging.info("lincludeChildren=%s" % lincludeChildren)
        
        lfutureKey = ndb.Key(urlsafe = lfutureKeyUrlSafe)
        
        lfuture = lfutureKey.get()
        
        def keymap(future, level):
            return future.key.urlsafe()
                
        lfutureJson = lfuture.to_dict(maxlevel=2 if lincludeChildren else 1, futuremapf = keymap) if lfuture else None
        
        if lfutureJson:
            lfutureJson["futurekey"] = lfutureJson["key"]
            del lfutureJson["key"]
    
            lchildren = lfutureJson.get("zchildren") or [];
            for lchild in lchildren:
                lchild["futurekey"] = lchild["key"]
                del lchild["key"]
            
        self.response.headers.add("Content-Type", "application/json")
        self.response.out.write(json.dumps(lfutureJson, indent=2))
