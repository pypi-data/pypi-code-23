#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# (c) 2010 by Ingo Weinzierl <ingo.weinzierl@intevation.de>
# (c) 2011, 2012, 2014 by Björn Ricks <bjoern.ricks@intevation.de>
# (c) 2017 Intevation GmbH
#   Author: Bernhard.Reiter@intevation.de
#
# This is Free Software licensed under the terms of GPLv3 or later.
# For details see LICENSE coming with the source of 'getan'.

import logging
import signal

from datetime import datetime, timedelta

from getan.resources import gettext as _
from getan.utils import human_time, safe_int

logger = logging.getLogger()


class State(object):
    """ Represents a State of Getan

    A State can be used to handle user input. The user input handling is done
    in three phases. First it is possible to filter keys that shouldn't be
    passed to a widget in input_filter. Afterwards it is possible to redirect
    a key to a specific widget in keypress. In the third phase it is possible
    to act on user input which isn't handled by a widget yet. The corresponing
    method is handle_input.

    Normally handle_input should be used to act on user input and change a
    state.
    """

    messages = {
    }

    def __init__(self, controller, view):
        self.controller = controller
        self.view = view
        self.config = controller.get_config()
        self.set_focus()

    def input_filter(self, input, raw):
        """Filters input that should not be passed to widget elements

        By default no input is filtered and input is returned unchanged.
        """
        return input

    def keypress(self, size, key):
        """Redirects user input to the current view"""
        self.view.keypress(size, key)

    def handle_input(self, input):
        """A derived State must implement handle_input"""
        raise NotImplementedError()

    def set_next_state(self, state):
        """Sets the next state"""
        self.controller.set_state(state)

    def msg(self, key):
        return self.messages[key]

    def set_focus(self):
        """ Override this method to set the focus when the state is created """
        pass


class ProjectState(State):

    def handle_input(self, input):
        keys = self.config.get_keybinding()
        logger.debug("ProjectState: handle input '%r'" % input)
        if keys.get_switch_time_mode() in input:
            self.view.switch_time_mode()
            return True

        if keys.get_switch_project_order() in input:
            self.view.switch_project_order()
            return True

        if keys.get_switch_lists() in input:
            if not self.controller.entries_view.rows:
                return True
            new_state = DefaultEntryListState(self, self.controller,
                                              self.controller.entries_view)
            self.set_next_state(new_state)
            return True

    def set_focus(self):
        self.controller.view.set_focus("projects")
        self.view.frame.set_focus("body")


class PausedProjectsState(ProjectState):

    messages = {
        'choose_proj': _('Choose a project: '),
    }

    def handle_input(self, key):
        logger.debug("PausedProjectsState: handle key '%r'" % key)
        keys = self.config.get_keybinding()
        ret = super(PausedProjectsState, self).handle_input(key)
        if ret:
            return True

        if keys.get_enter() in key:
            return self.select()

        if keys.get_insert() in key:
            state = AddProjectKeyState(self.controller, self.view)
            self.set_next_state(state)
            return True

        if keys.get_escape() in key:
            state = ExitState(self.controller, self.view)
            self.set_next_state(state)
            return True

        if keys.get_project_edit() in key:
            proj = self.view.item_in_focus()
            if not proj:
                return True
            state = ProjectEditKeyState(self.controller, self.view, proj)
            self.set_next_state(state)
            return True

        else:
            if len(key) > 0 and len(key[0]) == 1:
                state = SelectProjectState(self.controller, self.view)
                self.set_next_state(state)
                return state.handle_input(key)
        return False

    def select(self):
        proj = self.view.item_in_focus()
        self.controller.start_project(proj)
        state = RunningProjectsState(self.controller, self.view, proj)
        self.set_next_state(state)
        return True


class SelectProjectState(State):

    def __init__(self, controller, view):
        super(SelectProjectState, self).__init__(controller, view)
        self.proj_keys = ""
        self.set_footer_text()

    def reset(self):
        self.view.reset_footer()

    def set_footer_text(self):
        self.view.set_footer_text("Selecting project from key: %s" %
                                  self.proj_keys, "running")

    def check_key(self, key):
        return len(self.controller.find_projects_by_key(key))

    def select_project(self):
        proj = self.controller.project_by_key(self.proj_keys)
        if proj:
            self.reset()
            self.view.select_project(proj)
            self.controller.start_project(proj)
            self.controller.update_entries(proj)
            self.set_next_state(
                RunningProjectsState(self.controller, self.view,
                                     proj))
        return True

    def handle_input(self, key):
        keys = self.config.get_keybinding()
        if keys.get_escape() in key:
            self.reset()
            self.set_next_state(
                PausedProjectsState(self.controller, self.view))
            return True

        if 'backspace' in key:
            if len(self.proj_keys) > 0:
                self.proj_keys = self.proj_keys[:-1]
                self.set_footer_text()
            return True

        if keys.get_enter() in key:
            return self.select_project()

        else:
            if len(key) > 0 and len(key[0]) == 1:
                proj_key = self.proj_keys + key[0]
                num = self.check_key(proj_key)
                if num > 0:
                    self.proj_keys += key[0]
                    self.set_footer_text()
                    if num == 1:
                        # run project directly
                        return self.select_project()
        return False


class ExitState(ProjectState):

    messages = {
        'quit': _(" Really quit? (y/n)"),
        'choose': _(" Choose a project:")
    }

    def __init__(self, controller, view):
        super(ExitState, self).__init__(controller, view)
        self.controller.view.set_footer_text(self.msg('quit'), 'question')

    def handle_input(self, key):
        logger.debug("ExitState: handle key '%r'" % key)
        ret = super(ExitState, self).handle_input(key)
        if ret:
            return ret

        if 'y' in key or 'Y' in key:
            self.controller.exit()
            return True

        if 'n' in key or 'N' in key:
            self.controller.view.set_footer_text(
                self.msg('choose'), 'question')
            self.set_next_state(
                PausedProjectsState(self.controller, self.view))
            return True

        return False


class RunningProjectsState(ProjectState):

    messages = {
        'description': _("Enter a description: "),
        'add_time': _("Enter time to add [min]: "),
        'min_time': _("Enter time to subtract [min]: "),
        'continue': _("Press '%s' to continue."),
        'running': _("Running ( %s ) on '%s'."),
        'paused': _(" Break   ( %s ) %s."),
    }

    sec = 0
    break_start = None

    def __init__(self, controller, view, project):
        super(RunningProjectsState, self).__init__(controller, view)
        self.project = project
        self.view.deactivate_selection()
        signal.signal(signal.SIGALRM, self.handle_signal)
        signal.alarm(1)

    def handle_signal(self, signum, frame):
        proj = self.project
        keys = self.config.get_keybinding()

        if not proj:
            return

        if not self.break_start:
            self.controller.view.set_footer_text(self.msg('running') %
                                                 (human_time(self.sec),
                                                  proj.desc),
                                                 'running')
            self.controller.loop.draw_screen()
            self.sec = self.sec + 1
        else:
            self.view.set_footer_text(
                self.msg('paused') %
                (human_time((datetime.now() - self.break_start).seconds),
                 self.msg(
                     'continue') % keys.get_project_pause()),
                'paused_running')
            self.controller.loop.draw_screen()

        signal.signal(signal.SIGALRM, self.handle_signal)
        signal.alarm(1)

    def handle_input(self, key):
        logger.debug("RunningProjectsState: handle key '%r'" % key)
        keys = self.config.get_keybinding()
        ret = super(RunningProjectsState, self).handle_input(key)
        if ret:
            return ret

        if keys.get_enter() in key:
            return self.stop()

        if keys.get_add_time() in key:
            self.view.set_footer_text(self.msg('add_time'),
                                      'question', edit=True)
            self.set_next_state(AddTimeState(self.controller, self.view, self))
            return True

        if keys.get_subtract_time() in key:
            self.view.set_footer_text(self.msg('min_time'),
                                      'question', edit=True)
            self.set_next_state(SubtractTimeState(self.controller, self.view,
                                                  self))
            return True

        if keys.get_project_pause() in key:
            if not self.break_start:
                self.break_start = datetime.now()
            else:
                self.view.show_total_time()
                proj = self.project
                if proj:
                    proj.start += datetime.now() - self.break_start
                    self.break_start = None
                    signal.signal(signal.SIGALRM, self.handle_signal)
                    signal.alarm(1)
            return True
        return False

    def stop(self):
        signal.alarm(0)
        if self.break_start:
            proj = self.project
            if proj:
                proj.start += datetime.now() - self.break_start
        self.controller.view.set_footer_text(self.msg('description'),
                                             'question', edit=True)
        self.view.enable_selection()
        self.set_next_state(
            DescriptionProjectsState(
                self.controller, self.view,
                self, self.controller.view.get_frame().get_footer(),
                self.project))
        return True


class HandleUserInputState(State):

    def __init__(self, controller, view, state, footer):
        super(HandleUserInputState, self).__init__(controller, view)
        self.state = state
        self.footer = footer

    def handle_input(self, key):
        logger.debug("HandleUserInputState: handle key '%r'" % key)
        keys = self.config.get_keybinding()

        if keys.get_escape() in key:
            return self.exit()
        elif keys.get_enter() in key:
            return self.enter()
        return False

    def enter(self):
        raise Exception("Not implemented")

    def exit(self):
        # restore old focus
        self.state.set_focus()
        self.set_next_state(self.state)
        return True


class BaseTimeState(HandleUserInputState):

    def __init__(self, controller, view, running_state):
        super(BaseTimeState, self).__init__(controller, view, running_state,
                                            view.frame.get_footer())
        self.project = running_state.project

    def exit(self):
        self.view.show_total_time()
        return super(BaseTimeState, self).exit()

    def insert(self, key):
        if key[0] in ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']:
            self.footer.insert_text(key[0])
        else:
            logger.debug("BaseTimeState: invalid character for "
                         "adding/subtracting time: '%r'" % key)
        return True

    def set_focus(self):
        self.controller.view.set_focus("projects")
        self.view.frame.set_focus("footer")


class AddTimeState(BaseTimeState):

    def enter(self):
        minutes = safe_int(self.view.frame.get_footer().get_edit_text())
        project = self.project
        project.start -= timedelta(minutes=minutes)
        self.state.sec += minutes * 60
        logger.info("AddTimeState: add %d minutes to project '%s'"
                    % (minutes, project.desc))
        self.view.show_total_time()
        # set focus to the original element
        self.state.set_focus()
        self.set_next_state(self.state)
        return True


class SubtractTimeState(BaseTimeState):

    def enter(self):
        minutes = safe_int(self.view.frame.get_footer().get_edit_text())
        sec = minutes * 60
        if sec > self.state.sec:
            self.view.show_total_time()
            # set focus to the original element
            self.state.set_focus()
            self.set_next_state(self.state)
            return False
        project = self.project
        project.start += timedelta(minutes=minutes)
        self.state.sec -= sec
        logger.info("SubtractTimeState: subtract %d minutes from project '%s'"
                    % (minutes, project.desc))
        self.view.show_total_time()
        # set focus to the original element
        self.state.set_focus()
        self.set_next_state(self.state)
        return True


class DescriptionProjectsState(HandleUserInputState):

    """ Adds a description to a stopped running project """

    messages = {
        'choose_proj': _(" Choose a project."),
    }

    def __init__(self, controller, view, state, footer, project):
        super(DescriptionProjectsState, self).__init__(controller, view, state,
                                                       footer)
        self.project = project

    def keypress(self, size, key):
        """ Direct key to frame of GetanView """
        self.controller.view.frame.keypress(size, key)

    def enter(self):
        text = self.footer.get_edit_text()
        self.controller.stop_project(text)
        self.controller.view.set_footer_text(
            self.msg('choose_proj'), 'question')
        self.set_next_state(PausedProjectsState(self.controller, self.view))
        self.view.update_rows()
        self.view.show_total_time()
        return True

    def exit(self):
        if self.project:
            time = (datetime.now() - self.project.start).seconds
            self.state.sec = time
            signal.signal(signal.SIGALRM, self.state.handle_signal)
            signal.alarm(1)
        return super(DescriptionProjectsState, self).exit()

    def set_focus(self):
        self.controller.view.set_focus("footer")


class EntryListState(State):

    def __init__(self, state, controller, view):
        super(EntryListState, self).__init__(controller, view)
        self.projectlist_state = state

    def handle_input(self, key):
        logger.debug("EntryListState: pressed key '%r'" % key)
        keys = self.config.get_keybinding()

        if keys.get_switch_lists() in key:
            self.view.clear()
            self.set_next_state(self.projectlist_state)
            self.controller.view.set_focus(0)
            # Deletes the selection of entries
            self.view.selection = []
            return True

        if keys.get_enter() in key:
            return self.select()
        return False

    def select(self):
        self.view.select()
        return True

    def renew_focus(self):
        e_len = self.view.row_count()
        f = self.view.get_focus_pos()
        if f >= e_len:
            f = e_len - 1
        self.view.set_focus(f)

    def set_focus(self):
        self.controller.view.set_focus("entries")
        self.controller.entries_view.set_focus(0)


class DefaultEntryListState(EntryListState):

    def handle_input(self, key):
        logger.info("Handling DefaultEntryListState input")
        ret = super(DefaultEntryListState, self).handle_input(key)
        if ret:
            return ret

        keys = self.config.get_keybinding()
        if keys.get_escape() in key:
            self.view.clear()
            self.set_next_state(self.projectlist_state)
            self.controller.view.set_focus(0)
            return True

        if keys.get_entry_delete() in key:
            if self.view.selection:
                self.set_next_state(DeleteEntryState(self.projectlist_state,
                                                     self,
                                                     self.controller,
                                                     self.view))
            else:
                entry = self.view.item_in_focus()
                self.set_next_state(DeleteEntryState(self.projectlist_state,
                                                     self, self.controller,
                                                     self.view, [entry]))
            return True

        if keys.get_entry_move() in key:
            if self.view.selection:
                self.set_next_state(MoveEntryState(self.projectlist_state,
                                                   self.controller, self.view))
            else:
                entry = self.view.item_in_focus()
                self.set_next_state(MoveEntryState(self.projectlist_state,
                                                     self.controller,
                                                     self.view, [entry]))
            return True

        if keys.get_entry_edit() in key:
            entry = self.view.item_in_focus()
            if entry:
                self.set_next_state(EditEntryState(self.projectlist_state,
                                                   self.controller, self.view,
                                                   entry))
            return True

        if keys.get_entry_adjust() in key:
            entry = self.view.item_in_focus()
            if entry:
                self.set_next_state(AdjustEntryState(self.projectlist_state,
                                                     self.controller,
                                                     self.view, entry))
            return True

        if keys.get_entry_length() in key:
            entry = self.view.item_in_focus()
            if entry:
                self.set_next_state(LengthEntryState(self.projectlist_state,
                                                     self.controller,
                                                     self.view, entry))
            return True

        return False


class DeleteEntryState(EntryListState):

    messages = {
        'delete': _("Really delete this entry? (y/n)"),
    }

    def __init__(self, state, old_state, controller, view, entries=None):
        super(DeleteEntryState, self).__init__(state, controller, view)
        self.view.set_footer_text(self.msg('delete'), 'question')
        self.entries = entries
        self.old_state = old_state
        if not self.entries:
            self.entries = [x.item for x in self.view.selection]

    def handle_input(self, key):
        keys = self.config.get_keybinding()
        if 'y' in key:
            if self.entries:
                self.controller.delete_entries(self.entries)
                self.renew_focus()
            self.view.set_footer_text("", 'entry_footer')
            # avoid creating new DefaultEntryListState and setting focus
            self.set_next_state(self.old_state)
            self.controller.project_view.show_total_time()
            return True

        if 'n' in key or keys.get_escape() in key:
            self.view.set_footer_text("", 'entry_footer')
            # avoid creating new DefaultEntryListState and setting focus
            self.set_next_state(self.old_state)
            return True

        return False

    def set_focus(self):
        self.controller.view.set_focus("entries")


class MoveEntryState(EntryListState):
    messages = {
        'project': _(" Into which project do you want to move these entries?"),
        'really':  _(" Are you sure? (y/n)"),
    }

    proj = None

    def __init__(self, state, controller, view, entries=None):
        super(MoveEntryState, self).__init__(state, controller, view)
        self.view.set_footer_text(self.msg('project'), 'question')
        self.entries = entries
        self.proj_keys = ""
        self.project_view = controller.project_view
        if not self.entries:
            self.entries = [x.item for x in self.view.selection]

    def set_project_footer(self):
        self.project_view.set_footer_text("Selecting project from "
                                          "key: %s" % self.proj_keys,
                                          "running")

    def reset_project_footer(self):
        self.project_view.reset_footer()

    def check_key(self, key):
        return len(self.controller.find_projects_by_key(key))

    def select_project(self):
        proj = self.controller.project_by_key(self.proj_keys)
        if proj:
            self.proj = proj
            self.reset_project_footer()
            logger.debug("MoveEntryState: prepared entries to be "
                         "moved to project '%s'" % self.proj.desc)
            self.view.set_footer_text(self.msg('really'), 'question')

    def handle_input(self, key):
        keys = self.config.get_keybinding()
        if 'y' in key and self.proj:
            logger.debug("MoveEntryState: move selected entries.")
            self.controller.move_entries(self.entries, self.proj)
            self.renew_focus()
            self.view.set_footer_text('', 'entry_footer')
            self.proj = None
            self.set_next_state(DefaultEntryListState(self.projectlist_state,
                                                      self.controller,
                                                      self.view))
            return True

        if 'n' in key and self.proj:
            self.view.set_footer_text('', 'entry_footer')
            self.reset_project_footer()
            self.set_next_state(DefaultEntryListState(self.projectlist_state,
                                                      self.controller,
                                                      self.view))
            return True

        if keys.get_escape() in key:
            self.view.set_footer_text('', 'entry_footer')
            self.reset_project_footer()
            self.set_next_state(DefaultEntryListState(self.projectlist_state,
                                                      self.controller,
                                                      self.view))
            return True

        if 'backspace' in key:
            if len(self.proj_keys) > 0:
                self.proj_keys = self.proj_keys[:-1]
                self.set_project_footer()
            return True

        if keys.get_enter() in key and self.proj is None:
            self.select_project()
            return True

        if len(key) > 0 and len(key[0]) == 1 and self.proj is None:
            proj_key = self.proj_keys + key[0]
            num = self.check_key(proj_key)
            if num > 0:
                self.proj_keys = proj_key
                self.set_project_footer()
                if num == 1:
                    self.select_project()
            return True

        return False

    def set_focus(self):
        self.controller.view.set_focus("entries")


class AlterProjectState(HandleUserInputState):

    messages = {
        'choose_proj': _(' Choose a project.'),
    }

    def __init__(self, controller, view):
        super(AlterProjectState, self).__init__(
            controller, view, None,
            controller.view.get_frame().get_footer())

    def exit(self):
        self.controller.view.set_footer_text(self.msg('choose_proj'),
                                             'question')
        self.set_next_state(PausedProjectsState(self.controller, self.view))
        return True

    def keypress(self, size, key):
        """ Direct key to frame of GetanView """
        self.controller.view.frame.keypress(size, key)

    def set_focus(self):
        self.controller.view.set_focus("footer")


class AddProjectKeyState(AlterProjectState):

    messages = {
        'choose_proj': _(' Choose a project.'),
        'proj_key': _('Insert key for new project: '),
    }

    def __init__(self, controller, view):
        controller.view.set_footer_text(self.msg('proj_key'), 'question',
                                        edit=True)
        super(AddProjectKeyState, self).__init__(controller, view)

    def enter(self):
        key = self.footer.get_edit_text()
        if key == '':
            return True
        self.set_next_state(AddProjectDescriptionState(self.controller,
                                                       self.view, key))
        return True


class AddProjectDescriptionState(AlterProjectState):

    messages = {
        'proj_description': _('Insert a description for project: '),
        'choose_proj': _(" Choose a project.")
    }

    def __init__(self, controller, view, key):
        controller.view.set_footer_text(self.msg('proj_description'),
                                        'question', edit=True)
        super(AddProjectDescriptionState, self).__init__(controller, view)
        self.key = key

    def enter(self):
        description = self.footer.get_edit_text()
        if description == '':
            return self
        self.controller.add_project(self.key, description)
        self.exit()
        return True


class EditEntryState(HandleUserInputState):
    messages = {
        'edit_entry': _('Edit entry text: '),
    }

    def __init__(self, state, controller, view, entry):
        view.set_footer_text(self.msg('edit_entry'),
                             'question', True)
        super(EditEntryState, self).__init__(controller, view,
                                             None, view.footer)
        self.footer.set_edit_text(entry.desc)
        self.footer.set_edit_pos(len(self.footer.edit_text))
        self.entry = entry
        self.state = state
        logger.debug("EditEntryState: Entry %s" % entry)

    def enter(self):
        entry_desc = self.footer.get_edit_text()
        if entry_desc == '':
            return self
        entry = self.entry
        entry.desc = entry_desc
        self.controller.update_entry(entry)
        self.view.node_in_focus().update()
        return self.exit()

    def exit(self):
        self.view.set_footer_text("", 'entry_footer', False)
        self.set_next_state(DefaultEntryListState(self.state, self.controller,
                                                  self.view))
        return True

    def set_focus(self):
        self.controller.view.set_focus("entries")
        self.view.frame.set_focus("footer")


class AdjustEntryState(HandleUserInputState):
    messages = {
        'adjust_entry': _('Adjust datetime of entry: '),
    }

    def __init__(self, state, controller, view, entry):
        view.set_footer_text(self.msg('adjust_entry'),
                             'question', True)
        super(AdjustEntryState, self).__init__(controller, view,
                                               None, view.footer)

        # we only care up to seconds (which is 19 characters).
        # for usability the default value has to match the strptime fmt below.
        self.footer.set_edit_text(str(entry.start)[:19])
        self.footer.set_edit_pos(len(self.footer.edit_text))
        self.entry = entry
        self.state = state
        logger.debug("AdjustEntryState: Entry %s" % entry)

    def enter(self):
        entry_datetime = self.footer.get_edit_text()

        entry = self.entry
        duration = entry.get_duration()

        try:
            entry.start = datetime.strptime(entry_datetime,
                                            "%Y-%m-%d %H:%M:%S")
        except:
            return self

        entry.end = entry.start + duration

        self.controller.update_entry(entry)
        self.view.node_in_focus().update()
        return self.exit()

    def exit(self):
        self.view.set_footer_text("", 'entry_footer', False)
        self.set_next_state(DefaultEntryListState(self.state, self.controller,
                                                  self.view))
        return True

    def set_focus(self):
        self.controller.view.set_focus("entries")
        self.view.frame.set_focus("footer")


class LengthEntryState(HandleUserInputState):
    messages = {
        'adjust_length_entry': _('Adjust length of entry: '),
    }

    def __init__(self, state, controller, view, entry):
        view.set_footer_text(self.msg('adjust_length_entry'),
                             'question', True)
        super(LengthEntryState, self).__init__(controller, view,
                                               None, view.footer)

        # format current duration as string that is also accepted by enter()
        total_minutes = int(entry.get_duration().total_seconds()/60)
        hours = int(total_minutes // 60)

        if hours > 0:
            self.footer.set_edit_text(
                "{:d}:{:02d}".format(hours, int(total_minutes % 60)))
        else:
            self.footer.set_edit_text("{:d}".format(total_minutes))

        self.footer.set_edit_pos(len(self.footer.edit_text))
        self.entry = entry
        self.state = state
        logger.debug("LengthEntryState: Entry %s" % entry)

    def enter(self):
        """Changed the length of an entry.

        Works for total minutes or HH:MM.
        """
        entry_duration = self.footer.get_edit_text()

        # avoid unexpected behavior if minus signs are given in the new length
        if '-' in entry_duration:
            return self

        if ':' in entry_duration:
            hours, minutes = entry_duration.split(':')
        else:
            hours = 0
            minutes = entry_duration

        try:
            duration = timedelta(minutes=int(minutes), hours=int(hours))
        except:
            return self

        entry = self.entry
        entry.end = entry.start + duration

        self.controller.update_entry(entry)
        self.view.node_in_focus().update()
        return self.exit()

    def exit(self):
        self.view.set_footer_text("", 'entry_footer', False)
        self.set_next_state(DefaultEntryListState(self.state, self.controller,
                                                  self.view))
        return True

    def set_focus(self):
        self.controller.view.set_focus("entries")
        self.view.frame.set_focus("footer")


class ProjectEditKeyState(AlterProjectState):

    messages = {
        'proj_key': _('Insert key for project: '),
        'proj_description': _('Insert description for project: '),
        'choose_proj': _(" Choose a project.")
    }

    def __init__(self, controller, view, project):
        controller.view.set_footer_text(self.msg('proj_key'),
                                        'question', 1)
        super(ProjectEditKeyState, self).__init__(controller, view)
        self.project = project
        self.footer.set_edit_text(project.key)
        self.footer.set_edit_pos(len(self.footer.edit_text))

    def enter(self):
        key = self.footer.get_edit_text()
        if key == '':
            return True
        self.project.key = key
        self.set_next_state(ProjectEditDescriptionState(self.controller,
                                                        self.view,
                                                        self.project))
        return True


class ProjectEditDescriptionState(AlterProjectState):

    messages = {
        "proj_description": _("Insert description for project: "),
        "choose_proj": _(" Choose a project.")
    }

    def __init__(self, controller, view, project):
        controller.view.set_footer_text(self.msg("proj_description"),
                                        "question", 1)
        super(ProjectEditDescriptionState, self).__init__(controller, view)
        self.project = project
        self.footer.set_edit_text(project.desc)
        self.footer.set_edit_pos(len(self.footer.edit_text))

    def enter(self):
        description = self.footer.get_edit_text()
        if description == '':
            return self
        self.project.desc = description
        self.controller.update_project(self.project)
        self.controller.view.set_footer_text(
            self.msg('choose_proj'), 'question')
        self.set_next_state(PausedProjectsState(self.controller, self.view))
        return True
