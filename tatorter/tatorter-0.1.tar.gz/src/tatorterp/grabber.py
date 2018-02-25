# -*- coding: utf-8 -*-
# tatorter
# Copyright (C) 2018  Daniel Llin Ferrero
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''
Created on 04.02.2018

@author: DLF
'''

import mechanicalsoup as ms
import logging
from tatorterp import Episode
logger = logging.getLogger("tatorter")
logging.basicConfig()

team_to_location = {
    "Faber, Bönisch und Dalay":"Dortmund",
    "Sieland, Gorniak und Schnabel":"Dresden",
    "Ballauf und Schenk":"Köln",
    "Eisner und Fellner":"Wien",
    "Odenthal und Kopper":"Ludwigshafen",
    "Stellbrink und Marx":"Saarbrücken",
    "Lessing und Dorn":"Weimar",
    "Falke und Grosz":"Hamburg",
    "Thiel und Boerne":"Münster",
    "Lindholm":"Hannover",
    "Janneke und Brix":"Frankfurt",
    "Lürsen und Stedefreund":"Bremen",
    "Lannert und Bootz":"Stuttgart",
    "Batic und Leitmayr":"München",
    "Tobler und Berg":"Freiburg",
    "Flückiger und Ritschard":"Luzern",
    "Borowski und Brandt":"Kiel",
    "Rubin und Karow":"Berlin",
    "Faber, Bönisch, Dalay und Kossik":"Dortmund",
    "Voss, Ringelhahn, Goldwasser, Fleischer und Schatz":"Franken",
    "Blum und Perlmann, Matteo Lüthi":"Konstanz",
    "Blum und Perlmann":"Konstanz",
    "Saalfeld und Keppler":"Leipzig",
    "Flückiger und Lanning":"Luzern",
    "Eisner":"Wien",
    "Ritter und Stark":"Berlin",
    "Steier und Mey":"Frankfurt",
    "Murot":"Wiesbaden",
    "Batu":"Hamburg",
    "Kappl und Deininger":"Saarbrücken",
    "Saalfeld und Keppler /Ballauf und Schenk":"Leipzig-Köln",
    "Ballauf und Schenk /Saalfeld und Keppler":"Köln-Leipzig",
    "Tschiller und Gümer":"Hamburg",
    "Falke und Lorenz":"Hamburg",
    "Funck, Schaffert und Grewel":"Erfurt",
    "Steier":"Frankfurt",
    "Sieland, Gorniak, Mohr und Schnabel":"Dresden",
    "Berlinger":"Freiburg",
    "Borowski /Lindholm":"Kiel-Hannover",
    "Stark":"Berlin",
    "Schimanski und Thanner":"Duisburg"
    }

class WikipdediaDEGrabber(object):
    url = "https://de.wikipedia.org/wiki/Liste_der_Tatort-Folgen"
    def __init__(self):
        browser = ms.StatefulBrowser()
        browser.open(WikipdediaDEGrabber.url)
        tables = browser.get_current_page().find_all(name='table', attrs={'class':'wikitable sortable'})
        assert len(tables) == 2, "Page content unexpected, not exactly two wikitables. Cannot parse it."
        tbodys = tables[0].find_all("tbody")
        assert len(tbodys) == 1, "Page content unexpected, more than one tbody in wikitable. Cannot parse it."
        trs = tbodys[0].find_all("tr")
        logger.info("Parsing {} epsiode rows from {}.".format(len(trs), WikipdediaDEGrabber.url))
        self.episodes = []
        last_epsiode = None
        last_values = None
        for tr in trs[1:]:
            tds = tr.find_all('td')
            values = [td.text.split('(')[0].strip() for td in tds]
            episode_index = int(values[0].replace('a*','').replace('b*',''))
            # some special treatments
            if episode_index == 835:
                assert len(values) == 7
                values[6] = last_epsiode.author
                values.append(last_epsiode.director)
            elif episode_index in [854, 970]:
                assert len(values) == 5
                last_values[1] = values[1]
                last_values[3] = values[2]
                last_values[5] = values[3]
                values = last_values
            team = values[4]
            if team not in team_to_location:
                if episode_index > 800:
                    logger.warning("Location for team {} unknown and episode later than 800. Script should be updated!".format(team))
                location = "[{}]".format(team)
            else:
                location = team_to_location[team]
            episode = Episode(
                episode_index = episode_index,
                location = location,
                title = values[1],
                broadcaster = values[2],
                premiere = values[3],
                team = team,
                case_index = values[5],
                author = values[6],
                director = values[7]
            )
            self.episodes.append(episode)
            last_epsiode = episode
            last_values = values
            
                
        
        
#print (WikipdediaDEGrabber().episodes)

    