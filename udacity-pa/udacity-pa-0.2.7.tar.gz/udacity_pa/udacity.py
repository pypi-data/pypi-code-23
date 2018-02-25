from __future__ import absolute_import, division, print_function, unicode_literals
from future import standard_library
standard_library.install_aliases()
from builtins import input
from builtins import object
import sys
import os
import time
import requests
import json
import shutil
import copy
import zipfile
from itertools import cycle
from requests_toolbelt import MultipartEncoder, MultipartEncoderMonitor
from .uploadcallbacks import progressbar_callback
from .sessionbuilder import SessionBuilder, ProjectAssistantAuthenticationError


def default_app_data_dir():
  APPNAME = "udacity-pa"
  if sys.platform == 'win32':
    return os.path.join(os.environ['APPDATA'], APPNAME)
  else:
    return os.path.expanduser(os.path.join("~", "." + APPNAME))

class ProjectAssistantSubmissionError(Exception):
  def __init__(self, value):
    self.value = value
  def __str__(self):
    return self.value

def result_filename(project_name, submission_id):
  return "%s-result-%s.json" % (project_name, submission_id)

def submission_filename(project_name, submission_id):
  return "%s-%s.zip" % (project_name, submission_id)

PRESUBMIT_FILENAME = 'student.zip'

def root_url(environment):
  url = {'development': 'http://local-dev.udacity.com:3000',
         'staging': 'https://project-assistant-staging.udacity.com',
         'production': 'https://project-assistant.udacity.com'}

  return url[environment]

def build_session(environment = 'production', jwt_path = None):
  return SessionBuilder(root_url(environment), jwt_path).new()

#Zipfile helper function
def mkzip(root_path, zipfilename, filenames, max_zip_size):
  abs_root_path = os.path.abspath(root_path)
  abspaths = [os.path.abspath(x) for x in filenames]

  if os.path.commonprefix([abs_root_path] + abspaths) != abs_root_path:
    raise ProjectAssistantSubmissionError("Submitted files must in subdirectories of %s." % (root_path or "./"))

  with zipfile.ZipFile(zipfilename,'w') as z:
    for f in filenames:
      zpath = os.path.relpath(f, root_path)
      z.write(f, zpath)

  if os.stat(zipfilename).st_size > max_zip_size:
    raise ProjectAssistantSubmissionError("Your zipfile exceeded the limit of %d bytes" % max_zip_size)

def submit(nanodegree, 
           project, 
           filenames,
           environment = 'production', 
           max_zip_size = 8 << 20,
           jwt_path = None,
           refresh_time = 3):

    try:
      session = build_session(environment, jwt_path)
    except ProjectAssistantAuthenticationError as e:
      print(e)
      return
    
    submission = Submission(nanodegree,
                            project,
                            session,
                            filenames,
                            max_zip_size = max_zip_size,
                            upload_progress_callback = progressbar_callback,
                            environment = environment)

    print("Submission includes the following files:")
    print('\n'.join(['    ' + f for f in submission.filenames]))
    print("")

    print("Uploading submission...")
    try:
      submission.submit()
    except ProjectAssistantSubmissionError as e:
      print('\n' + str(e))
      return

    print('\n')
    wheel = cycle(['|', '/', '-', '\\'])
    spin_freq = 8.
    while not submission.poll():
      for _ in range(int(refresh_time * spin_freq)):
        sys.stdout.write("\rWaiting for results... {}".format(next(wheel)))
        sys.stdout.flush()
        time.sleep(1. / spin_freq)
    sys.stdout.write("\rWaiting for results...Done!\n\n")

    print("Results:\n--------")
    if submission.feedback():
      if submission.console():
        print(submission.console())

      rfilename = result_filename(submission.project_name(), submission.id())
      sfilename = submission_filename(submission.project_name(), submission.id())

      with open(rfilename, "w") as fd:
        json.dump(submission.feedback(), fd, indent=4, separators=(',', ': '))

      print("\nDetails are available in %s.\n" % rfilename)
      print("If you would like this version of the project to be reviewed,\n" \
            "submit %s to the reviews website.\n" %  (sfilename))

    elif submission.error_report():
        print(json.dumps(submission.error_report(), indent=4))
        print("For help troubleshooting, please see the FAQ:\n https://project-assistant.udacity.com/faq")
    else:
        print("Unknown error.")


#Submissions for Nanodegrees
class Submission(object):
  def __init__(self, 
               nanodegree, 
               project,
               session,
               filenames,
               max_zip_size = 8 << 20,
               upload_progress_callback = None,
               environment = 'production'):

    self.nanodegree = nanodegree
    self.project = project
    self.environment = environment

    self.s = session
    self.filenames = copy.deepcopy(filenames)
    self.max_zip_size = max_zip_size
    self.upload_progress_callback = upload_progress_callback or default_upload_progress_callback

  def project_name(self):
    return self.project

  def _get_submit_url(self):
    return root_url(self.environment) + "/student/nanodegree/%s/project/%s/submission" % (self.nanodegree, self.project)   

  def _get_poll_url(self):
    return root_url(self.environment) + "/student/submissions/%s" % (self.id())

  def submit(self):

    self.submit_url = self._get_submit_url()

    mkzip(os.getcwd(), PRESUBMIT_FILENAME, self.filenames, self.max_zip_size)

    fd = open(PRESUBMIT_FILENAME, "rb")

    m = MultipartEncoder(fields={'zipfile': ('student.zip', fd, 'application/zip')})
    monitor = MultipartEncoderMonitor(m, self.upload_progress_callback)

    try:
      r = self.s.post(self.submit_url, 
                      data=monitor,
                      headers={'Content-Type': monitor.content_type})
      r.raise_for_status()
    except requests.exceptions.HTTPError as e:
      if r.status_code == 403:
        raise ProjectAssistantSubmissionError("You don't have access to this project.")
      elif r.status_code in [404,429,500]:
        try:
          response_json = r.json()
          message = response_json.get("message") or "An internal server error occurred."
        except:
          message = "An unknown error occurred"
        raise ProjectAssistantSubmissionError(message)
      else:
        raise

    fd.close()

    self.submission = r.json()

    shutil.move(PRESUBMIT_FILENAME,
                submission_filename(self.project_name(), self.id()))

  def poll(self):
    r = self.s.get(self._get_poll_url())
    r.raise_for_status()

    self.submission = r.json()

    return self.submission['feedback'] is not None or self.submission['error_report'] is not None

  def result(self):
    return self.feedback()

  def feedback(self):
    return self.submission['feedback']

  def console(self):
    return self.submission['console']

  def error_report(self):
    return self.submission['error_report']

  def id(self):
    return self.submission['id']
