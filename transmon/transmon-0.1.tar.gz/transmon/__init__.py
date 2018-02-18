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
import sys
import json
from .project import Project
from .fetcher import GitFetcher
from .analyzer import AndroidAnalyzer

def main():
    if(len(sys.argv) < 2):
        print('Usage: ' + sys.argv[0] + ' projects-file')
        sys.exit(1)
    with open(sys.argv[1]) as f:
        conf = json.load(f)
        res = []
        for proj in conf:
            if proj['fetcher'] == 'git':
                f = GitFetcher()
            else:
                raise Exception('No such fetcher: ' + proj['fetcher'])
            if proj['analyzer'] == 'android':
                a = AndroidAnalyzer()
            else:
                raise Exception('No such analyzer: ' + proj['analyzer'])
            p = Project(proj['name'], f, proj['uri'], a, proj['home-page'])
            p.fetch()
            res.append({"name": proj['name'], 'home-page': proj['home-page'],
                'state': p.analyze()})
            p.cleanup()
        print(json.dumps(res))
