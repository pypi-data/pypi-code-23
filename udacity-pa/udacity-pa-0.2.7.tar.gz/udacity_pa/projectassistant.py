from __future__ import absolute_import, division, print_function, unicode_literals
from future import standard_library
standard_library.install_aliases()
from builtins import input
from builtins import object

import os
import sys
import argparse
import errno
import requests
import json
from urllib.request import getproxies
from io import StringIO

from pkg_resources import Requirement, resource_filename

from .udacity import build_session, root_url, result_filename, submission_filename
from .sessionbuilder import default_jwt_paths

class NotProjectAssistantError(Exception):
  """Exception raised when not an Udacity Project Assistant directory."""

  def __init__(self):
    super(NotProjectAssistantError, self).__init__("Not an Udacity Project Assistant directory. No .udacity-pa folder found.")

pa_dir = os.path.join(os.path.realpath(os.getcwd()),'.udacity-pa')
if not os.path.isfile(os.path.join(pa_dir,'projects.py')):
  raise  NotProjectAssistantError()

try:
  sys.path.append(pa_dir)
  import projects
  projects.nanodegree
  projects.projects
  projects.submit
except:
  raise ValueError(".udacity-pa/projects.py file is invalid.")

class ActionHelper(object):
  def __init__(self, args):
    self.environment = args.environment
    self.jwt_path = args.jwt_path
    self.root_url = root_url(self.environment)

  def build_session(self):
    return build_session(self.environment, self.jwt_path)

class GetHelper(ActionHelper):
  def __init__(self, args):
    super(GetHelper, self).__init__(args)

    self.submission_id = args.submission_id

  def get_url(self):
    return self.root_url + "/student/submissions/%s" % self.submission_id

  def act(self):
    http = self.build_session()

    url = self.get_url()

    r = http.get(url)
    r.raise_for_status()

    submission = r.json()

    zipfile_url = submission['zipfile']['url']
    project_name = submission['project_name']

    #Downloading the zipfile
    local_zip_filename = submission_filename(project_name, submission['id'])
    r = requests.get(zipfile_url, stream=True)
    with open(local_zip_filename, 'wb') as f:
        for chunk in r.iter_content(chunk_size=1024): 
            if chunk:
                f.write(chunk)
    
    print(submission['console'])

    local_result_filename = result_filename(project_name, submission['id'])

    with open(local_result_filename, "w") as fd:
      try:
        json.dump(submission['feedback'], fd, indent=4, separators=(',', ': '))
      except:
        fd.write(submission['feedback'])

    print("\nDetails available in %s.\n" % local_result_filename)
    print("If you would like this version of the project to be reviewed,\n" \
          "submit %s to the reviews website.\n" %  local_zip_filename)


class LSHelper(ActionHelper):
  def __init__(self, args, ndkey):
    super(LSHelper, self).__init__(args)

    self.ndkey = ndkey
    self.project_name = args.project_name

  def ls_url(self):
    return self.root_url + "/student/nanodegree/%s/project/%s" % (self.ndkey, self.project_name)

  def act(self):
    http = self.build_session()

    url = self.ls_url()

    r = http.get(url)
    r.raise_for_status()

    output = StringIO()
    date_header = '{:40s}'.format('Submission Time')
    id_header = 'ID'.rjust(9)
    output.write('%s %s' % (date_header, id_header))
    output.write('\n' + '-' * 50)
    for s in r.json():
      date = '{:40s}'.format(s['created_at'][:39])
      s_id = ("%d" % s['id']).rjust(9)
      output.write('\n%s %s' % (date, s_id))

    print(output.getvalue())

class SubmitHelper(ActionHelper):
  def __init__(self, args):
    super(SubmitHelper, self).__init__(args)

    self.args = args

  def act(self):
    projects.submit(self.args)

class DiagnoseHelper(object):
  def __init__(self, args):
    self.args = args

  def act(self):
    data = {
      'proxies' : getproxies(),
      'default_jwt_paths': default_jwt_paths(),
      'jwt_present': any(os.path.isfile(jwt_path) for jwt_path in default_jwt_paths()),
      'projects_file_present': os.path.isfile(os.path.join(os.path.realpath(os.getcwd()),
                                                    '.udacity-pa',
                                                    'projects.py')),
      'terminal': os.environ.get('TERM'),
      'platform': sys.platform
    }
    json.dump(data, sys.stdout, indent=4)

def main(args, nanodegree):
  if args.action == 'ls':
    return LSHelper(args, nanodegree).act()
  elif args.action == 'get':
    return GetHelper(args).act()
  elif args.action == 'submit':
    return SubmitHelper(args).act()
  elif args.action == 'diagnose':
    return DiagnoseHelper(args).act()

def main_func():

  parser = argparse.ArgumentParser(description='CLI for submitting projects to the udacity project assistant')

  parser.add_argument('--environment', default='production', help="webserver environment")
  parser.add_argument('--jwt_path', default=None, help="path to file containing auth information")

  subparsers = parser.add_subparsers(dest="action", help="Action")

  ls_parser = subparsers.add_parser("ls")
  ls_parser.add_argument('project_name', 
                         choices = projects.projects, 
                         default = projects.projects[0],
                         nargs = '?',
                         help="project name")

  get_parser = subparsers.add_parser("get")
  get_parser.add_argument('submission_id', help="submission_id")

  submit_parser = subparsers.add_parser("submit")
  submit_parser.add_argument('args', nargs=argparse.REMAINDER)

  diagnose_parser = subparsers.add_parser("diagnose")
  diagnose_parser.add_argument('args', nargs=argparse.REMAINDER)

  args = parser.parse_args()

  main(args, projects.nanodegree)

  return 0
