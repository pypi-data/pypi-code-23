#!/usr/bin/env python

from __future__ import print_function

'''
Copyright 2017 Peach Tech

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
'''

"""
Peach API Security: Automate traffic generation commands
Copyright (c) Peach Tech

Run one or more commands that generate traffic through Peach API Security.
This script can be used as a traffic generator with Peach API Security by
running commands (like curl) that generate HTTP(S) traffic.

Installation:

  Installation of this tool has two steps.
  
  1. Install Python
  2. Install dependencies

    pip install -r requirements.txt
  
  3. Start using the tool

CI Integration:

  To better support redteam usage, this traffic generator
  does not need to be run from the CI integration script.
  If no CI runner is detected it will automatically create
  a new testing job.

Syntax:

  peachrunner 
  peachrunner folder scripts/*.sh
  peachrunner textfiles commands.txt
  peachrunner cmd "curl http://api.foo.com/v1/users"

"""

try:
	import click
	from requests import Request, Session
	import peachapisec
except:
	print("Error, missing dependencies.")
	print("Use 'pip install -r requirements.txt'")
	exit(-1)

import os
import glob
import atexit
import subprocess
import sys
import struct
import zipfile
import json

try:
	from urlparse import urlparse
	from urlparse import urljoin
	from urlparse import ParseResult
except:
	from urllib.parse import urlparse
	from urllib.parse import urljoin
	from urllib.parse import ParseResult

try:
	from BaseHTTPServer import BaseHTTPRequestHandler
except:
	from http.server import BaseHTTPRequestHandler

_verbose = 0

def _msg(level, msg):
	if level <= _verbose:
		print(msg)

def _get_environ(key, default):
	if key in os.environ:
		return os.environ[key]
	
	return default

def _put_environ(key, value):
	if not value:
		return
	
	os.environ[str(key)] = str(value)

__session_id = None
def _atexit_cleanup():
	'''Make sure we cleanup on forced exit
	'''

	try:
		if __session_id:
			peachapisec.session_teardown()
	except:
		pass

atexit.register(_atexit_cleanup)

def _parse_headers(header_strings):
	'''Convert a list of 'key: value' strings into dict
	'''
	
	headers = {}
	for hs in header_strings:
		key, value = hs.split(':', 1)
		headers[key.strip()] = value.strip()
	
	return headers


# ################################################################################
# ################################################################################
# ################################################################################


class HttpArchiveReader(object):

	def __init__(self, har_file):
		if not os.path.exists(har_file):
			raise Exception("Error, file '%s' does not exist" % har_file)
		
		self.har_file = har_file

	def _headers_from_request(self, request):

		headers = {}
		for header in request['headers']:
			headers[header['name']] = header['value']

		return headers

	def _body_from_request(self, request):

		bodySize = int(request['bodySize'])
		if bodySize == 0:
			return None
		
		if 'postData' in request and 'text' in request['postData']:
			return request['postData']['text']

		raise Exception('Error: Unable to locate body in request: \n%s' % json.dumps(request))

	def requests(self):
		
		with open(self.har_file, "r") as fd:
			har = json.loads(fd.read())

		if not 'log' in har:
			raise Exception("Error, file '%s' is missing the 'log' section." % self.har_file)

		if not 'entries' in har['log']:
			raise Exception("Error, file '%s' is missing the 'log.entries' section." % self.har_file)
		
		entries = har['log']['entries']

		if len(entries) == 0:
			raise Exception("Error, file '%s' has zero entries in 'log.entries'." % self.har_file)

		for entry in entries:

			request = entry['request']

			# Note: The request['url'] contains query string

			req = Request(
				request['method'], 
				request['url'],
				data=self._body_from_request(request), 
				headers=self._headers_from_request(request))

			name = "%s %s" % (request['method'], request['url'])

			yield (req, name)



class PostmanReader(object):

	def __init__(self, postman_file):
		if not os.path.exists(postman_file):
			raise Exception("Error, file '%s' does not exist" % postman_file)
		
		self.postman_file = postman_file
		
	def _body_from_request(self, item):

		body = item['body']

		if not 'mode' in body:
			return None

		if 'raw' in body:
			return body['raw']

		elif 'file' in body:
			fname = body['file']['src']
			if not os.path.exists(fname):
				raise Exception("Error, file specified in postman collection '%s' does not exist" % fname)
			
			with open(fname, 'r') as fd:
				return fd.read()

		raise Exception('Error, unsupported body type "%s" in collection.  Please contact support.' % body['mode'])
	
	def _headers_from_request(self, request):
		headers = {}
		for header in request['header']:
			headers[header['key']] = header['value']
		
		return headers
	
	def requests(self):
		with open(self.postman_file,'r') as fd:
			coll = json.load(fd)

		try:
			items = coll['item']
		except:
			raise Exception("Error, expected 'item' property in root object.")

		try:
			cnt = 0
			while cnt < len(items):
				item = items[cnt]
				cnt += 1

				if 'item' in item:
					items += item['item']

				elif 'request' in item:
					request = item['request']

					url = request['url']['raw'] if isinstance(request['url'], dict) else request['url']
					req = Request(
						request['method'], 
						url,
						data=self._body_from_request(request), 
						headers=self._headers_from_request(request))

					name = item['name'] if 'name' in item else "%s %s" % (request['method'], url)

					yield (req, name)
		except:
			raise Exception("Please contact support and provide your Postman Collection for reivew.")


class BurpReader(object):
	REQ_TAG  = b'<request>'
	RESP_TAG = b'<response>'
	SSL_TAG = b'<https>'

	DEBUG = False

	# there is probably a nicer way to do this ... ;-/
	def len_str_to_len(self, len_str):
		result = 0
		length = len(len_str)
		for i in range(0, length):
			byte = struct.unpack('B', len_str[i:i+1])[0]
			result += byte << (8 * (length - 1 - i))
		return result

	def __init__(self, burp_file):
		'''Create a new BurpReader, providing burp file to read
		'''

		if not os.path.exists(burp_file):
			raise Exception("Error, file '%s' does not exist" % burp_file)
		
		self.burp_file = burp_file

	def is_https(self, content, req_index):
		'''Is current request https?
		'''

		tag = self.SSL_TAG

		index = content.rindex(tag, 0, req_index)

		length_field_length = struct.unpack('B', content[index+len(tag):index+len(tag)+1])[0]
		if self.DEBUG: _msg(0, 'length_field_len: ' + str(length_field_length))

		length_str = content[index+len(tag)+1:index+len(tag)+1+length_field_length]
		if self.DEBUG: _msg(0, 'length_str: ' + str(length_str))

		value = self.len_str_to_len(length_str)

		return value != 60


	def requests(self):
		'''Generator yielding all requests found in burp file

		Note: Using some code found online.  It's very waistfull of memory.
		'''

		z = zipfile.ZipFile(self.burp_file, 'r')
		f = z.open('burp', 'r')
		content = f.read()
		f.close()
		z.close()

		index = 0
		i = 0
		
		while True:

			if self.DEBUG: _msg(0, str(index))
			
			tag = self.REQ_TAG
			if (i % 2 == 1):
				tag = self.RESP_TAG
			
			try:
				# look for <request>, <response> alternating
				index = content.index(tag, index)
			except ValueError:
				# substring not found, we are done
				break

			# format:
			# <request>bllll$content</request>
			# b is length of length field
			# llll is length field of $content (4 in this example)
			length_field_length = struct.unpack('B', content[index+len(tag):index+len(tag)+1])[0]
			if self.DEBUG: _msg(0, 'length_field_len: ' + str(length_field_length))

			length_str = content[index+len(tag)+1:index+len(tag)+1+length_field_length]
			if self.DEBUG: _msg(0, 'length_str: ' + str(length_str))
			
			length = self.len_str_to_len(length_str)
			
			if self.DEBUG: _msg(0, 'length: ' + str(length))
			if self.DEBUG: _msg(0, 'content: ' + content[index+len(tag)+1+length_field_length:index+len(tag)+1+length_field_length+length])
			
			req = content[index+len(tag)+1+length_field_length:index+len(tag)+1+length_field_length+length]
			yield (req, self.is_https(content, index))

			index = index+len(tag)+1+length_field_length+length+1


class HTTPRequest(BaseHTTPRequestHandler):
	'''Use standard python libraries to parse
	HTTP request.

	# Using this new class is really easy!

	request = HTTPRequest(request_text)

	print request.error_code       # None  (check this first)
	print request.command          # "GET"
	print request.path             # "/who/ken/trust.html"
	print request.request_version  # "HTTP/1.1"
	print len(request.headers)     # 3
	print request.headers.keys()   # ['accept-charset', 'host', 'accept']
	print request.headers['host']  # "cm.bell-labs.com"
	'''

	def __init__(self, scheme, base_url, headers, request_text):
		'''Create HTTRequest object

		 * scheme: 'http' or 'https'
		 * base_url: None, or url prefix
		 * headers: None, or array of header strings to add ('key: value')
		 * request_text: raw request to parse
		'''

		try: # Python 2.7
			from StringIO import StringIO
			self.rfile = StringIO(request_text)
			self.raw_requestline = self.rfile.readline()
			self.error_code = self.error_message = None
			self.scheme = scheme
			self.parse_request()

		except: # Python 3
			from io import BytesIO
			self.rfile = BytesIO(request_text)
			self.raw_requestline = self.rfile.readline()
			self.error_code = self.error_message = None
			self.scheme = scheme
			self.parse_request()

		content_len = int(self.headers['Content-Length'] if 'Content-Length' in self.headers else 0)
		self.body = self.rfile.read(content_len) if content_len > 0 else None

		if base_url:
			url = urlparse(base_url)
			self.host = url.netloc
			self.url = urljoin(base_url, self.path)
		else:
			self.host = self.headers['Host']
			self.url = "%s://%s%s" % (self.scheme, self.host, self.path)

		self.headers['Host'] = self.host

		try: # python 2.7
			self.headers = self._parse_headers(self.headers.headers)
		
		except: # python 3
			hdrs = {}
			for k in self.headers:
				v = self.headers[k]
				hdrs[k] = v
			self.headers = hdrs

		hdict = _parse_headers(headers)
		for h in hdict.keys():
			self.headers[h] = hdict[h]

	def as_request(self):
		'''Convert to a prepared requests request
		'''

		if 'Host' in self.headers:
			del self.headers['Host']

		req = Request(
			self.command, 
			self.url,
			data=self.body, 
			headers=self.headers)

		return req.prepare()
		

	def send_error(self, code, message):
		self.error_code = code
		self.error_message = message


class CommandRunner(object):
	'''Command line runner.
	'''

	def __init__(self, cmd):
		'''cmd is a command line to execute
		'''
		self.cmd = cmd

	def __str__(self):
		'''short name for this item
		'''

		return self.cmd

	def run(self, proxy):
		try:
			out = subprocess.check_output(self.cmd, shell=True, stderr=subprocess.STDOUT)
			_msg(2, out)
		
		except subprocess.CalledProcessError as e:
			_msg(1, str(e))
			_msg(2, e.output)


class RequestRunner(object):
	'''Request runner
	'''

	def __init__(self, name, request):
		'''request is a PreparedRequest object
		'''

		self.request = request
		self.name = name if name else "%s %s" % (self.request.method, self.request.url)

	def __str__(self):
		'''short name for this item
		'''

		return self.name

	def run(self, proxy):
		'''Send request
		'''

		_msg(2, "      Request: %s %s" % (self.request.method, self.request.url))
		
		try:
			s = Session()
			resp = s.send(self.request,
				verify=False,
				proxies= {'http':proxy, 'https':proxy},
				#timeout=timeout
			)

			_msg(2, "      Response code: %s" % resp.status_code)
			_msg(3, resp.text)
		except Exception as e:
			_msg(1, str(e))
			


# ################################################################################
# ################################################################################
# ################################################################################

@click.group(help="Run one or more commands that generate traffic through Peach API Security.")
@click.option("--ci/--no-ci", default=False, help="Running from CI script, ensure no auto start.")
@click.option('-a', "--api", help="Peach API Security API URL. Defaults to PEACH_API environ.")
@click.option('-t', "--api_token", help="Peach API Security API Token. Defaults to PEACH_API_TOKEN environ.")
@click.option('-p',"--project", help="Peach API Security project to use. Ex. Default")
@click.option('-r', "--profile", help="Peach API Security profile to use. Ex. Quick")
@click.option("--dryrun/--no-dryrun", default=False, help="Try operation with out Peach API Security")
@click.option('-v', count=True, help="Increase verbosity of output. Supply more than once to continue increasing.")
@click.pass_context
def cli(ctx, ci, api, api_token, project, profile, dryrun, v, **kwargs):

	ctx.obj['DRY_RUN'] = dryrun
	ctx.obj['CI'] = ci or _get_environ('PEACH_PROXY', None)
	ctx.obj['VERBOSE'] = v

	global _verbose
	_verbose = 0
	if v:
		_verbose = v

	if ctx.obj['CI']:
		_msg(0, "* Detected we are running from CI")
	else:
		_msg(0, "* Detected we are not running from CI, will try and start job")

		if not api:
			_msg(0, "Error, set PEACH_API or provide --api argument")
			exit(1)

		if not api_token:
			_msg(0, "Error, set PEACH_API_TOKEN or provide --api argument")
			exit(1)

		if not project:
			_msg(0, "Error, set PEACH_PROJECT or provide --project argument")
			exit(1)

		if not profile:
			_msg(0, "Error, set PEACH_PROFILE or provide --profile argument")
			exit(1)

		peachapisec.set_peach_api(api)
		peachapisec.set_peach_api_token(api_token)

	ctx.obj['API'] = api
	ctx.obj['API_TOKEN'] = api_token
	ctx.obj['PROJECT'] = project
	ctx.obj['PROFILE'] = profile

	_put_environ('PEACH_API', api)
	_put_environ('PEACH_API_TOKEN', api_token)
	_put_environ('PEACH_PROJECT', project)
	_put_environ('PEACH_PROFILE', profile)


def _run(ctx, name, scripts):
	global __session_id

	if not ctx.obj['CI']:

		_msg(0, "* Running directly, starting testing job")

		if not ctx.obj['DRY_RUN']:
			peachapisec.session_setup(
				ctx.obj['PROJECT'], 
				ctx.obj['PROFILE'], 
				ctx.obj['API'])

			__session_id = peachapisec.session_id()

	proxy = None
	if not ctx.obj['DRY_RUN']:
		proxy = peachapisec.proxy_url()

		_put_environ("HTTP_PROXY", proxy)
		_put_environ("HTTPS_PROXY", proxy)

	_msg(0, "* Found %d %s to run as test cases." % (len(scripts), name))
	_msg(0, "")

	total = len(scripts)
	call_cnt = 0
	for cnt in range(total):
		script = scripts[cnt]

		_msg(0, "  - Testing with '%s'..." % script)

		state = 'Continue'
		while state == 'Continue':
			call_cnt += 1
			_msg(1, "  - [%d/%d]: '%s'" % (cnt+1, total, script))

			if not ctx.obj['DRY_RUN']:
				peachapisec.setup()
				peachapisec.testcase(script)
			
			script.run(proxy)

			if not ctx.obj['DRY_RUN']:
				state = peachapisec.teardown()
			else:
				state = "NextTest"
	

	_msg(0, "")
	
	if call_cnt > total:
		_msg(0, "* A total of %d %s have been run" % (call_cnt, name))

	else:
		_msg(0, "ERROR: Testing has not completed correctly.")
		_msg(0, "  Please verify requests are proxied through")
		_msg(0, "  Peach API Security correctly. The environmental")
		_msg(0, "  variable HTTP_PROXY and HTTPS_PROXY are set with")
		_msg(0, "  the proxy URL.")

	if not ctx.obj['DRY_RUN']:
		peachapisec.suite_teardown()

	if not ctx.obj['CI']:
		_msg(0, "* Stopping testing session")

		if not ctx.obj['DRY_RUN']:
			state = peachapisec.session_state()
			if state == 'Error':
				try:
					reason = peachapisec.session_error_reason()
					_msg(0, "* Session failed: %s" % reason)
				except:
					_msg(0, "* Session failed due to unknwon reason")

			__session_id = None
			peachapisec.session_teardown()


@cli.command(help="Run set of scripts in a folder")
@click.option('-v', count=True, help="Increase verbosity of output. Supply more than once to continue increasing.")
@click.argument('folder')
@click.pass_context
def folder(ctx, v, folder, **kwargs):

	if v and v > 0:
		global _verbose
		_verbose += v

	_msg(0, "* Running all scripts in '%s'" % folder)

	scripts = glob.glob(folder)
	if len(scripts) == 0:
		_msg(0, "Error, no files found in '%s'" % folder)
		exit(-1)

	runners = []
	for script in scripts:
		runners.append(CommandRunner(script))

	_run(ctx, "scripts", runners)


@cli.command(help="Run set of commands from text file.")
@click.option('-v', count=True, help="Increase verbosity of output. Supply more than once to continue increasing.")
@click.argument('input')
@click.pass_context
def textfile(ctx, v, input, **kwargs):

	if v and v > 0:
		global _verbose
		_verbose += v

	if not os.path.exists(input):
		_msg(0, "Error, file '%s' does not exist" % input)
		exit(1)

	with open(input, "rb") as fd:
		scripts = fd.read()
		
		try:
			scripts.decode('utf-8')
		except:
			pass
		
		scripts = scripts.splitlines()

	if len(scripts) == 0:
		_msg(0, "Error, no commands found in file")
		exit(-1)

	_msg(0, "* Running %d commands from file" % len(scripts))

	runners = []
	for script in scripts:
		runners.append(CommandRunner(script))

	_run(ctx, "commands", runners)

@cli.command(help="Run single command")
@click.option('-v', count=True, help="Increase verbosity of output. Supply more than once to continue increasing.")
@click.argument('command')
@click.pass_context
def cmd(ctx, v, command, **kwargs):

	if v and v > 0:
		global _verbose
		_verbose += v

	_msg(0, "* Running command: %s" % command)

	_run(ctx, "commands", [CommandRunner(command)])


@cli.command(help="Replay recorded requests from Burp project")
@click.option("-u","--base-url", help="Base url for requests.  This overrides the recorded base url. Ex: '-u http://api.foo.com', '-u http://api.foo.com:7777'")
@click.option("--header", "-H", multiple=True, help="Provide header. Multiple header arguments can be provided. Ex: '-H \"Header: Value\"'")
@click.option('-v', count=True, help="Increase verbosity of output. Supply more than once to continue increasing.")
@click.argument('input')
@click.pass_context
def burp(ctx, base_url, header, v, input, **kwargs):

	if not os.path.exists(input):
		_msg(0, "Error, file '%s' does not exist" % input)
		exit(1)

	if v and v > 0:
		global _verbose
		_verbose += v

	if base_url:
		try:
			url_base = urlparse(base_url)

			assert(len(url_base.scheme) > 0)
			assert(len(url_base.netloc) > 0)

		except Exception as e:
			_msg(0, "")
			_msg(0, "Error, base url not in correct format.")
			_msg(0, "")
			_msg(0, "Please verify the base url supplied via -u or --base-url is in the")
			_msg(0, "expected format as shown below:")
			_msg(0, "")
			_msg(0, "  Format: -u http://api.foo.com")
			_msg(0, "")
			exit(-1)
	
	try:
		# Verify headers are provided correctly
		_parse_headers(header)
	except Exception as e:
		_msg(0, "")
		_msg(0, "Error parsing headers supplied on the command line.")
		_msg(0, "Please make sure all headers are in the correct format:")
		_msg(0, "")
		_msg(0, "  Format: -H \"Header: Value\"")
		_msg(0, "")
		_msg(0, "Exception: "+str(e))
		exit(-1)

	try:
		runners = []
		burp = BurpReader(input)
		for req_raw, is_https in burp.requests():

			scheme = 'https' if is_https else 'http'
			req = HTTPRequest(scheme, base_url, header, req_raw)
			runners.append(RequestRunner(None, req.as_request()))
	except Exception as e:
		_msg(0, "")
		_msg(0, "Error reading Burp file.")
		_msg(0, str(e))
		_msg(0, "")
		exit(-1)
	

	if len(runners) == 0:
		_msg(0, "Error, no requests found in BURP file")
		exit(-1)

	_msg(0, "* Sending %d requests from BURP file" % len(runners))

	_run(ctx, "request", runners)


@cli.command(help="Replay recorded requests from exported Postman collection")
@click.option("-u","--base-url", help="Base url for requests.  This overrides the recorded base url. Ex: '-u http://api.foo.com', '-u http://api.foo.com:7777'")
@click.option("--header", "-H", multiple=True, help="Provide header. Multiple header arguments can be provided. Ex: '-H \"Header: Value\"'")
@click.option('-v', count=True, help="Increase verbosity of output. Supply more than once to continue increasing.")
@click.argument('input')
@click.pass_context
def postman(ctx, base_url, header, v, input, **kwargs):

	if not os.path.exists(input):
		_msg(0, "Error, file '%s' does not exist" % input)
		exit(1)

	if v and v > 0:
		global _verbose
		_verbose += v

	if base_url:
		try:
			url_base = urlparse(base_url)

			assert(len(url_base.scheme) > 0)
			assert(len(url_base.netloc) > 0)

		except Exception as e:
			_msg(0, "")
			_msg(0, "Error, base url not in correct format.")
			_msg(0, "")
			_msg(0, "Please verify the base url supplied via -u or --base-url is in the")
			_msg(0, "expected format as shown below:")
			_msg(0, "")
			_msg(0, "  Format: -u http://api.foo.com")
			_msg(0, "")
			exit(-1)

	try:
		headers = _parse_headers(header)
	except Exception as e:
		_msg(0, "")
		_msg(0, "Error parsing headers supplied on the command line.")
		_msg(0, "Please make sure all headers are in the correct format:")
		_msg(0, "")
		_msg(0, "  Format: -H \"Header: Value\"")
		_msg(0, "")
		_msg(0, "Exception: "+str(e))
		exit(-1)
	
	try:
		runners = []
		postman = PostmanReader(input)
		for req, name in postman.requests():

			if base_url:
				url_base = urlparse(base_url)
				url = urlparse(req.url)

				req.url = ParseResult(url_base.scheme, url_base.netloc, url.path, url.params, url.query, url.fragment).geturl()

			if 'Host' in req.headers:
				del req.headers['Host']

			for k in headers.keys():
				req.headers[k] = headers[k]

			runners.append(RequestRunner(name, req.prepare()))
	except Exception as e:
		_msg(0, "")
		_msg(0, "Error processing Postman collection.")
		_msg(0, str(e))
		_msg(0, "")
		exit(-1)

	if len(runners) == 0:
		_msg(0, "Error, no requests found in Postman collection file")
		exit(-1)

	_msg(0, "* Sending %d requests from Postman collection" % len(runners))

	_run(ctx, "request", runners)
	

@cli.command(help="Replay recorded requests from exported HTTP Archive (.har)")
@click.option("-u","--base-url", help="Base url for requests.  This overrides the recorded base url. Ex: '-u http://api.foo.com', '-u http://api.foo.com:7777'")
@click.option("--header", "-H", multiple=True, help="Provide header. Multiple header arguments can be provided. Ex: '-H \"Header: Value\"'")
@click.option('-v', count=True, help="Increase verbosity of output. Supply more than once to continue increasing.")
@click.argument('input')
@click.pass_context
def har(ctx, base_url, header, v, input, **kwargs):

	if not os.path.exists(input):
		_msg(0, "Error, file '%s' does not exist" % input)
		exit(1)

	if v and v > 0:
		global _verbose
		_verbose += v

	try:
		headers = _parse_headers(header)
	except Exception as e:
		_msg(0, "")
		_msg(0, "Error parsing headers supplied on the command line.")
		_msg(0, "Please make sure all headers are in the correct format:")
		_msg(0, "")
		_msg(0, "  Format: -H \"Header: Value\"")
		_msg(0, "")
		_msg(0, "Exception: "+str(e))
		exit(-1)
	
	try:

		har = HttpArchiveReader(input)
		runners = []
		for req, name in har.requests():

			if base_url:
				try:
					url_base = urlparse(base_url)

					url = urlparse(req.url)

					assert(len(url_base.scheme) > 0)
					assert(len(url_base.netloc) > 0)

					req.url = ParseResult(url_base.scheme, url_base.netloc, url.path, url.params, url.query, url.fragment).geturl()

				except Exception as e:
					_msg(0, "")
					_msg(0, "Error, base url not in correct format.")
					_msg(0, "")
					_msg(0, "Please verify the base url supplied via -u or --base-url is in the")
					_msg(0, "expected format as shown below:")
					_msg(0, "")
					_msg(0, "  Format: -u http://api.foo.com")
					_msg(0, "")
					exit(-1)

			if 'Host' in req.headers:
				del req.headers['Host']

			for k in headers.keys():
				req.headers[k] = headers[k]

			runners.append(RequestRunner(name, req.prepare()))

	except Exception as e:
		_msg(0, "")
		_msg(0, "Error processing the provided HTTP Archive (HAR) file.")
		_msg(0, str(e))
		_msg(0, "")
		exit(-1)


	if len(runners) == 0:
		_msg(0, "Error, no requests found in HAR archive file")
		exit(-1)

	_msg(0, "* Sending %d requests from HAR archive" % len(runners))

	_run(ctx, "request", runners)

def run():
	cli(obj={}, auto_envvar_prefix='PEACH')

if __name__ == '__main__':

	_msg(0, "")
	_msg(0, "Peach API Security: Automate Commands")
	_msg(0, "~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
	_msg(0, "")
	run()


# end
