#!/usr/bin/env python3
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
Created on 05.02.2018

@author: DLF
'''
from os.path import expanduser
from datetime import datetime
from pathlib import Path
from shutil import move
import argparse
import logging
import json
import glob
import sys
import os
from tatorterp import Episode, Matcher
from tatorterp.grabber import WikipdediaDEGrabber

logger = logging.getLogger("tatorter")
logging.basicConfig()
logger.setLevel(logging.INFO)

file_rename_pattern = "{episode_index:0>4}--{location}--{title}--({team})"

def start():
    # get arguments
    home = expanduser("~")
    default_cache_path = "{}/.tatorter.cache".format(home)
    argparser = argparse.ArgumentParser()
    argparser.add_argument(
        "-c","--cache",
        help="file for caching episode data (default: {})".format(default_cache_path),
        default=default_cache_path
        )
    argparser.add_argument(
        "-r","--renew-cache",
        help="force the cache file to be renewed, even it is not out-dated".format(default_cache_path),
        action='store_true'
        )
    argparser.add_argument(
        "files",
        nargs='*'
        )
    args = argparser.parse_args()
    
    # options, not configurable
    cache_days = 1
    
    cache_path = Path(args.cache)
    cache_used = False
    episodes = None
    
    # handle cache, load data (from cache or Wikipdeia)
    if args.renew_cache:
        logger.info("Forcing cache update.")
    else:
        if cache_path.is_file():
            last_modified_date = datetime.fromtimestamp(os.path.getmtime(cache_path))
            now = datetime.now()
            if (now - last_modified_date).days < cache_days:
                cache_used = True
                logging.info("Loading cache...")
                with open(cache_path,mode="r",encoding="utf-8") as cache_file:
                    cache = json.load(cache_file)
                    episodes = []
                    for e in cache:
                        episodes.append(Episode(**e))
            else:
                logger.info("Cache out-dated. ({} days)".format((now - last_modified_date).days))
        else:
            logger.info("No cache file.")
    if not cache_used:
        logging.info("Fetching online data...")
        episodes = WikipdediaDEGrabber().episodes
        logger.info("Storing cache...")
        with open(cache_path,mode="w",encoding="utf-8") as cache_file:
            json.dump([episode.as_dict for episode in episodes], cache_file)
    
    # identify files to process
    files = []
    for f in args.files:
        files.extend(glob.glob(f))
    
    # handle each file separately
    options_count = 5
    for file in files:
        matcher = Matcher(file, episodes)
        source_file = os.path.basename(file)
        target_path = os.path.dirname(file)
        target_extension = os.path.splitext(file)[1]
        target_names = []
        print ("="*80)
        print ("Choose new name for \"{}\"".format(source_file)) 
        for ix in range(options_count):
            match = matcher.match_list[ix]
            target_name = file_rename_pattern.format(**(match[1].as_dict)) + target_extension
            target_name = target_name.replace("/","⁄")
            target_names.append(target_name)
            print ("–"*80 + "\n" + "{ix:>5} {match:>6}| {target_name}".format(
                ix=ix+1,
                match="({}%)".format(match[0]),
                target_name = target_name
                ))
        selection = None
        while selection is None:
            print ("–"*80)
            selection_text = input("Choose a new file name ([1..{max}]), skip this file (s) or cancel this script (q):".format(max=options_count))
            if selection_text in [str(i+1) for i in range(options_count)]:
                selection = int(selection_text)
            if selection_text in ['s', 'q']:
                selection = selection_text
        if selection == 's':
            continue
        if selection == 'q':
            sys.exit(0)
        full_target_name = os.path.join(target_path, target_names[selection-1])
        if Path(full_target_name).is_file():
            selection_text = input("Target file {} exists! Overwrite? (y/n)".format(full_target_name))
            while selection_text.lower() not in ['y','n']:
                selection_text = input("I just understand 'y' or 'n'. Overwrite? (y/n)".format(full_target_name))
            if selection_text == 'n':
                continue
        try:
            move(file, full_target_name)
            print ("Moved to {}".format(full_target_name))
        except IOError as e:
            print("File could not be copied ({0}): {1}".format(e.errno, e.strerror))   
        print ("")


if __name__ == "__main__":
    start()
    
    