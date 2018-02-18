#   Copyright (c) 2018 Julien Lepiller <julien@lepiller.eu>
#
#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU Affero General Public License as
#   published by the Free Software Foundation, either version 3 of the
#   License, or (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU Affero General Public License for more details.
#
#   You should have received a copy of the GNU Affero General Public License
#   along with this program.  If not, see <https://www.gnu.org/licenses/>.
####
import tempfile
import pygit2

class Fetcher(object):
    def __init__(self):
        self.path = None
        return

    def fetch(self, project):
        raise Exception('Not implemented')

    def getDirectory(self):
        if self.path == None:
            return None
        return self.path.name

class GitFetcher(Fetcher):
    def __init__(self):
        Fetcher.__init__(self)

    def fetch(self, uri):
        path = tempfile.TemporaryDirectory()
        self.path = path
        pygit2.clone_repository(uri, path.name)
        return path.name

    def cleanup(self):
        self.path.cleanup()
        self.path = None
