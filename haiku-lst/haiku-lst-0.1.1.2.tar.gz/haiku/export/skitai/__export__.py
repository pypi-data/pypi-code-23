import os
import skitai
from skitai.saddle import Saddle
import json
import codecs
from haiku import Haiku, StandardAnalyzer
import haiku

app = Saddle (__name__)

def getdir (*d):
	return os.path.join (app.config.resource_dir, *d)

def is_json (request):
	return request.command == "post" and not request.get_header ('content-type', '').startswith ('application/x-www-form-urlencoded')

def error (response, status, errcode, errmsg = "", errstack = None):
	err = response.fault (errmsg, errcode, exc_info = errstack)
	return response (status, err)
	
#-----------------------------------------------------------------

@app.before_mount
def before_mount (wasc):
	analyzer = StandardAnalyzer (200, stem_level = 2, make_lower_case = 1, numthread = len (wasc.threads))
	for alias in os.listdir (getdir ("haikus")):
		wasc.logger.get ("app").log ('loading haiku model: %s' % alias)
		model = Haiku (getdir ("haikus", alias), haiku.CL_L2, analyzer)
		haiku.models.add (alias, model)
  
@app.umounted
def umounted (wasc):
	haiku.models.close ()

#-----------------------------------------------------------------

@app.before_request
def before_request (was):
	if was.request.args.get ('alias') and not haiku.models.get (was.request.args ['alias']):
		return error (was.response, "404 Not Found", 40400)		

@app.failed_request
def failed_request (was, exc_info):
  return error (
  	was.response, 
  	"500 Internal Server Error", 
  	50000, 
  	errstack = app.debug and exc_info or None
  )

#-----------------------------------------------------------------

@app.route ("/")
def index (was):
	return was.response.api ({'collections': haiku.models.names ()})

@app.route ("/<alias>/guess", methods = ["GET", "POST", "OPTIONS"])
def guess (was, alias, **args):
	# args: q = '', l = 'un'
	q = args.get ("q")
	if not q:
		return error (was.response, "400 Bad Request", 40003, 'parameter q required')
	l = args.get ("l", 'un')	
	if type (q) is list:
		return was.response.api ([haiku.models.get (alias).guess (eq, l) for eq in q])
	return was.response.api ({"result": haiku.models.get (alias).guess (q, l,)})
	

if __name__ == "__main__":

	pref = skitai.pref ()
	pref.use_reloader = 1
	pref.debug = 1
	
	config = pref.config	
	config.resource_dir = skitai.joinpath ('resources')	
	skitai.mount ("/v1", (haiku, "app"), "app", pref)
	skitai.run (port = 5005)
