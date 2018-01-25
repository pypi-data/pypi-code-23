from __future__ import with_statement
import cPickle, os, xmlrpclib, time, urllib2, httplib, socket
from xml.etree import ElementTree
from functools import partial
import xml.parsers.expat
import sqlite

# library config
pypi = 'pypi.python.org'
BASE = 'https://'+pypi
SIMPLE = BASE + '/simple/'
version = '0.2'
UA = 'pip_mirror/'+version

# package filter
package_filter_count = [0]
def package_filter(pkg,st=None):
    if st is not None and not st.quiet:
        global package_filter_count
        if package_filter_count[0] == 0:
            print "package_filter: started filtering OSS-only packages"
        if package_filter_count[0] % 500 == 0:
            print "package_filter: processed %d packages" % package_filter_count[0]
        package_filter_count[0] += 1

    try:
        last_release = xmlrpc().package_releases(pkg)[-1]
    except IndexError:
        # if no releases available, ignore this package
        return False
    rel_data = xmlrpc().release_data(pkg,last_release) 

    osi_approved = False
    for c in rel_data['classifiers']:
        if c.startswith('License :: OSI Approved'):
            osi_approved = True

    if not osi_approved:
        if (rel_data['license'] in set(['BSD','GPL','MIT','ZPL 2.1','LGPL','GPLv3',
          'MIT License','BSD License','GPL version 2','ZPL','PSF',
          'Apache License 2.0','Apache 2.0','GPL-3','Apache','MIT license',
          'Apache License, Version 2.0','GPLv3+','gpl','Apache Software License',
          'LGPLv3','Public Domain','Simplified BSD','GPLv2','GPL2','MIT/X11',
          'GPL v3','GNU GPL v3','GNU GPL-3 or later','GNU GPL v2','GNU LGPL',
          'GPL v2','GNU General Public License (GPL)',
          'GNU LESSER GENERAL PUBLIC LICENSE, Version 3','New BSD License','LGPL v3',
          'GPL3','The MIT License (MIT)','GNU Lesser General Public License (LGPL)',
          'GNU LESSER GENERAL PUBLIC LICENSE, Version 2.1','Apache2','GNU GPL, GNU LGPL',
          'WTFPL','LGPL License','Public Domain (WTFPL)','GPL3, see LICENSE.txt',
          'CDDL','BSD 3 Clause','3-clause BSD','AGPLv3','New BSD license',
          'GNU General Public License version 3.0 (GPLv3)','GNU GPLv2',
          'Apache License','GNU GPL v2 or later','Boost Software License','MPL',
          'BSD (3-clause)','http://www.fsf.org/licensing/licenses/lgpl.txt',
          'BSD-style license','GNU LGPL v.3','LGPLv2+','LGPLv3+','GNU Public License v3',
          'http://www.apache.org/licenses/LICENSE-2.0','public domain',
          'GNU General Public License version 3 or later','GPL 2',
          'GNU Lesser General Public License','LGPL-3.0',
          'MIT License, Zope Public License (rest.py), BSD License (odict.py)',
          'License :: OSI Approved :: MIT License','Simplified BSD License',
          'AGPLv3 or Permissive for use with Open Source databases','GPL version 3',
          ])):
            osi_approved = True
    return osi_approved

# Helpers

_proxy = None
def xmlrpc():
    global _proxy
    if _proxy is None:
        _proxy = xmlrpclib.ServerProxy(BASE+'/pypi')
        _proxy.useragent = UA
    return _proxy

_conn = None
def http():
    global _conn
    if _conn is None:
        _conn = httplib.HTTPSConnection(pypi)
        _conn.connect()
    # check that connection is still open
    try:
        if not _conn.sock:
            # HTTPS server had announced to close the connection
            raise socket.error
        _conn.sock.getpeername()
    except socket.error:
        _conn = httplib.HTTPSConnection(pypi)
        _conn.connect()
    return _conn

def now():
    return int(time.time())

# Main class

class Synchronization:
    "Picklable status of a mirror"

    def __init__(self):
        self.homedir = None
        self.quiet = False
        
        # time stamps: seconds since 1970
        self.last_completed = 0 # when did the last run complete
        self.last_started = 0   # when did the current run start

        self.complete_projects = set()
        self.projects_to_do = set()

        self.skip_file_contents = False

    def defaults(self):
        # Fill fields that may not exist in the pickle
        for field, value in (('quiet', False),):
            if not hasattr(self, field):
                setattr(self, field, value)

    def store(self):
        with open(os.path.join(self.homedir, "status"), "wb") as f:
            cPickle.dump(self, f, cPickle.HIGHEST_PROTOCOL)
            self.storage.commit()

    @staticmethod
    def load(homedir, storage=None):
        res = cPickle.load(open(os.path.join(homedir, "status"), "rb"))
        res.storage = storage or sqlite.SqliteStorage(os.path.join(homedir, "files"))
        res.defaults()
        res.homedir = homedir # override pickled value in case it got relocated
        return res

    #################### Synchronization logic ##############################

    @staticmethod
    def initialize(targetdir, storage=None):
        'Create a new empty mirror. This operation should not be interrupted.'
        if not os.path.exists(targetdir):
            os.makedirs(targetdir)
        else:
            assert not os.listdir(targetdir)
        for d in ('simple', 'packages', 'serversig',
                  'local-stats/days'):
            os.makedirs(os.path.join(targetdir, 'web', d))
        status = Synchronization()
        status.homedir = targetdir
        status.last_started = now()
        status.projects_to_do = set(xmlrpc().list_packages())
        status.projects_to_do = set( filter(partial(package_filter,st=status), status.projects_to_do) )
        status.storage = storage or sqlite.SqliteStorage(os.path.join(status.homedir, "files"))
        status.store()
        return status

    def synchronize(self):
        # check whether another job is already running
        pid = self.storage.find_running()
        if pid:
            # check whether process still runs
            try:
                os.kill(pid, 0)
            except OSError:
                # process is gone, take over
                self.storage.end_running()
            else:
                self.storage.commit()
                if not self.quiet:
                    print "Currently already running; mirroring is skipped"
                return
        self.storage.start_running(os.getpid())
        self.storage.commit()
        try:
            self._synchronize()
        finally:
            self.storage.end_running()
            self.storage.commit()

    def _synchronize(self):
        'Run synchronization. Can be interrupted and restarted at any time.'
        if self.last_started == 0:
            # no synchronization in progress. Fetch changelog
            self.last_started = now()
            changes = xmlrpc().changelog(self.last_completed-1)
            if not changes:
                self.update_timestamp(self.last_started)
                return
            for change in changes:
                self.projects_to_do.add(change[0])
            self.projects_to_do = set( filter(partial(package_filter,st=self), self.projects_to_do) )
            self.copy_simple_page('')
            self.store()
        # sort projects to allow for repeatable runs
        for project in sorted(self.projects_to_do):
            if not project:
                # skip empty project names resulting from PyPI-wide changes
                continue
            if not self.quiet:
                print "Synchronizing", project.encode('utf-8')
            data = self.copy_simple_page(project)
            if not data:
                self.delete_project(project)
                self.store()
                continue
            try:
                files = set(self.get_package_files(data))
            except xml.parsers.expat.ExpatError, e:
                # not well-formed, skip for now
                if not self.quiet:
                    print "Page for %s cannot be parsed: %r" % (project, e)
                raise
            for file in files:
                if not self.quiet:
                    print "Copying", file
                self.maybe_copy_file(project, file)
            # files start with /; remove it
            relfiles = set(p[1:] for p in files)
            for file in self.storage.files(project)-relfiles:
                    self.remove_file(file)
            self.complete_projects.add(project)
            self.projects_to_do.remove(project)
            self.store()
        self.update_timestamp(self.last_started)
        self.last_completed = self.last_started
        self.last_started = 0
        self.store()

    def update_timestamp(self, when):
        with open(os.path.join(self.homedir, "web", "last-modified"), "wb") as f:
            f.write(time.strftime("%Y%m%dT%H:%M:%S\n", time.gmtime(when)))

    def copy_simple_page(self, project):
        project = project.encode('utf-8')
        h = http()
        if project:
             h.putrequest('GET', '/simple/'+urllib2.quote(project)+'/')
        else:
             h.putrequest('GET', '/simple/')
        h.putheader('User-Agent', UA)
        h.endheaders()
        r = h.getresponse()
        html = r.read()
        if r.status == 404:
            return None
        if r.status == 301:
            # package not existant anymore, however, similarly-spelled
            # package exists
            return None
        if r.status != 200:
            raise ValueError, "Status %d on %s" % (r.status, project)
        project_simple_dir = os.path.join(self.homedir, 'web', 'simple', project)
        if not os.path.exists(project_simple_dir):
            os.mkdir(project_simple_dir)
        with open(os.path.join(project_simple_dir, 'index.html'), "wb") as f:
            f.write(html)
        h.putrequest('GET', '/serversig/'+urllib2.quote(project)+'/')
        h.putheader('User-Agent', UA)
        h.endheaders()
        r = h.getresponse()
        sig = r.read()
        if r.status != 200:
            if not project:
                # index page is unsigned
                return
            raise ValueError, "Status %d on signature for %s" % (r.status, project)
        with open(os.path.join(self.homedir, "web", "serversig", project), "wb") as f:
            f.write(sig)
        return html

    def get_package_files(self, data):
        x = ElementTree.fromstring(data)
        res = []
        for a in x.findall(".//a"):
            url = a.attrib['href']
            if not url.startswith('../../packages/'):
                continue
            url = url.split('#')[0]
            url = url[len('../..'):]
            res.append(url)
        return res

    def maybe_copy_file(self, project, path):
        h = http()
        if self.skip_file_contents:
            h.putrequest("HEAD", urllib2.quote(path))
        else:
            h.putrequest("GET", urllib2.quote(path))
        h.putheader('User-Agent', UA)
        etag = self.storage.etag(path)
        if etag:
            h.putheader("If-none-match", etag)
        h.endheaders()
        r = h.getresponse()
        if r.status == 304:
            # not modified, discard data
            r.read()
            return
        if path.startswith("/"):
            path = path[1:]
        lpath = os.path.join(self.homedir, "web", path)
        if r.status == 200:
            self.storage.remove_file(path) # readd when done downloading
            data = r.read()
            dirname = os.path.dirname(lpath)
            if not os.path.exists(dirname):
                os.makedirs(dirname)
            with open(lpath, "wb") as f:
                f.write(data)
            # XXX may set last-modified timestamp on file
            if "etag" in r.msg:
                self.storage.add_file(project, path, r.msg['etag'])
            self.store()
            return
        if r.status == 404:
            self.remove_file(path)

    def remove_file(self, path):
        self.storage.remove_file(path)
        lpath = os.path.join(self.homedir, "web", path)
        if os.path.exists(lpath):
            os.unlink(lpath)

    def delete_project(self, project):
        for f in self.storage.files(project):
            self.remove_file(f)
        project_simple_dir = os.path.join(self.homedir, "web", "simple", project)
        if os.path.exists(project_simple_dir):
            index_file = os.path.join(project_simple_dir, "index.html")
            if os.path.exists(index_file):
                os.unlink(index_file)
            os.rmdir(project_simple_dir)
        project_serversig_dir = os.path.join(self.homedir, "web", "serversig", project)
        if os.path.exists(project_serversig_dir):
            os.unlink(project_serversig_dir)
        if project in self.projects_to_do:
            self.projects_to_do.remove(project)
        if project in self.complete_projects:
            self.complete_projects.remove(project)
