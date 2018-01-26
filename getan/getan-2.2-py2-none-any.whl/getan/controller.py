# -*- coding: utf-8 -*-
#
# (c) 2010 by Ingo Weinzierl <ingo.weinzierl@intevation.de>
# (c) 2011 by Björn Ricks <bjoern.ricks@intevation.de>
#
# A python worklog-alike to log what you have 'getan' (done).
#
# This is Free Software licensed under the terms of GPLv3 or later.
# For details see LICENSE coming with the source of 'getan'.
#

import logging
import urwid

from datetime import datetime

from getan.view import GetanView, ProjectList, EntryList
from getan.states import PausedProjectsState
from getan.utils import format_time
from getan.config import Config

logger = logging.getLogger()


class GetanController(object):

    def __init__(self, backend):
        self.config = Config()

        self.backend = backend
        projects, entries = self.load_projects()
        self.projects = projects
        self.running = []

        self.view = None
        self.entries_view = EntryList(entries)
        self.project_view = ProjectList(self, self.projects)

        self.view = GetanView(self, self.project_view, self.entries_view)
        self.state = PausedProjectsState(self, self.project_view)

    def main(self):
        theme = self.config.get_theme()
        self.loop = urwid.MainLoop(self.view,
                                   theme.get_palette(),
                                   screen=urwid.raw_display.Screen(),
                                   input_filter=self.input_filter)
        self.loop.run()

    def input_filter(self, input, raw_input):
        if 'window resize' in input:
            self.loop.screen_size = None
            self.loop.draw_screen()
        else:
            input = self.state.input_filter(input, raw_input)
            self.loop.process_input(input)
            self.state.handle_input(input)

    def load_projects(self):
        projects = self.backend.load_projects()
        if projects:
            entries = self.backend.load_entries(projects[0].id)
        else:
            entries = []
        return (projects, entries)

    def update_entries(self, project):
        logger.debug("GetanController: update entries for project %s." %
                     project.id)

        project.load_entries()

        if self.view:
            self.view.update_entries(project.entries)

    def move_entries(self, entries, project):
        old_project = self.project_by_id(entries[0].project_id)
        self.backend.move_entries(entries, project.id)
        self.update_entries(old_project)
        self.project_view.update_rows()

    def delete_entries(self, entry_nodes):
        if not entry_nodes:
            return
        proj_id = entry_nodes[0].project_id
        proj = self.project_by_id(proj_id)
        if proj:
            entries = entry_nodes
            self.backend.delete_entries(entries)
            self.update_entries(proj)

    def project_by_key(self, key):
        for proj in self.projects:
            if proj.key == key:
                return proj
        return None

    def project_by_id(self, id):
        for proj in self.projects:
            if proj.id == id:
                return proj
        return None

    def find_projects_by_key(self, key):
        projects = []
        for proj in self.projects:
            if proj.key.startswith(key):
                projects.append(proj)
        return projects

    def start_project(self, project):
        if not project:
            return
        self.running.append(project)
        project.start = datetime.now()
        logger.info("Start project '%s' at %s."
                    % (project.desc, format_time(datetime.now())))
        self.view.set_footer_text(" Running on '%s'" % project.desc, 'running')
        logger.debug('All running projects: %r' % self.running)

    def stop_project(self, desc=None, display=True):
        desc = desc or '-no description-'
        if not self.running:
            return
        project = self.running.pop()
        if not project:
            return
        logger.info("Stop project '%s' at %s."
                    % (project.desc, format_time(datetime.now())))
        project.stop = datetime.now()
        self.backend.insert_project_entry(project, datetime.now(), desc)
        if display:
            self.update_entries(project)
        logger.debug('Still running projects: %r' % self.running)

    def add_project(self, key, description):
        if not key or not description:
            return
        self.backend.insert_project(key, description)
        self.update_projects()

    def update_entry(self, entry):
        self.backend.update_entry(entry)

    def shutdown(self):
        for project in self.running:
            self.stop_project(display=False)

    def update_project(self, project):
        self.backend.update_project(project)
        self.update_projects()

    def update_projects(self):
        projects, entries = self.load_projects()
        self.projects = projects
        self.project_view.load_rows(projects)
        self.project_view.total_time()

    def get_config(self):
        return self.config

    def set_state(self, state):
        self.state = state

    def exit(self):
        logger.info("GetanController: exit.")
        raise urwid.ExitMainLoop()
