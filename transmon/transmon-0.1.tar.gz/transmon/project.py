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


class Project(object):
    def __init__(self, name, fetcher, uri, analyzer, homepage):
        self.name = name
        self.fetcher = fetcher
        self.uri = uri
        self.analyzer = analyzer
        self.homepage = homepage
        self.dir = None

    def fetch(self):
        self.fetcher.fetch(self.uri)

    def analyze(self):
        return self.analyzer.analyze(self.fetcher.getDirectory())

    def cleanup(self):
        self.fetcher.cleanup()
