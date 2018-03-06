# -*- coding: utf-8 -*-
# copyright 2016 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
# contact http://www.logilab.fr -- mailto:contact@logilab.fr
#
# This program is free software: you can redistribute it and/or modify it under
# the terms of the GNU Lesser General Public License as published by the Free
# Software Foundation, either version 2.1 of the License, or (at your option)
# any later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU Lesser General Public License for more
# details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

"""cubicweb-celerytask entity's classes"""
import six

import celery
from celery.result import AsyncResult, from_serializable

from cubicweb import NoResultError
from cubicweb.entities import AnyEntity, fetch_config
from cubicweb.view import EntityAdapter
from cubicweb.predicates import is_instance
from cubicweb.server.hook import DataOperationMixIn, Operation

from cw_celerytask_helpers import redislogger as loghelper

from cubes.celerytask import STATES, FINAL_STATES

_ = six.text_type

_TEST_TASKS = {}
UNKNOWN_TASK_NAME = six.text_type('<unknown>')


def get_tasks():
    """Return tasks to be run (for use in cubicweb test mode)"""
    return _TEST_TASKS.copy()


def run_all_tasks(cnx):
    """Run all pending tasks (for use in cubicweb test mode)"""
    results = {}
    # run all tasks and gather results.
    # Tasks can create other tasks, so run them until there is no one left.
    while _TEST_TASKS:
        task_eid = list(_TEST_TASKS)[0]
        task = _TEST_TASKS.pop(task_eid)
        # Ensure current task id is in the scope of the current test
        if task.id is not None and not cnx.execute(
            'Any X WHERE X is CeleryTask, X task_id %(task_id)s',
            {'task_id': task.id}
        ):
                continue
        results[task_eid] = task.delay()

    if celery.current_app.conf.CELERY_ALWAYS_EAGER:
        for task_eid, result in results.items():
            wf = cnx.entity_from_eid(task_eid).cw_adapt_to('IWorkflowable')
            transition = {
                STATES.SUCCESS: 'finish',
                STATES.FAILURE: 'fail',
            }[result.state]
            comment = result.traceback
            if comment is not None and not isinstance(comment, six.text_type):
                comment = comment.decode('utf-8')
            wf.fire_transition(transition, comment)
    return results


def sync_task_state(cnx, task_id, task_name):
    log = CeleryTaskAdapter
    task_id = six.text_type(task_id)
    result = AsyncResult(task_id)
    if result.state == 'PENDING':
        log.info('Task %s state is unknown', task_id)
        return
    try:
        task = cnx.find('CeleryTask', task_id=task_id).one()
    except NoResultError:
        task = cnx.create_entity('CeleryTask', task_id=task_id,
                                 task_name=task_name or UNKNOWN_TASK_NAME)
        log.info('Created <CeleryTask %s (task_id %s)>',
                 task.eid, task_id)
    task.cw_adapt_to('ICeleryTask').sync_state(task_id, task_name)


def start_async_task(cnx, task, *args, **kwargs):
    """Create and start a new task

    `task` can be either a task name, a task object or a task signature
    """
    task_name = six.text_type(celery.signature(task).task)
    entity = cnx.create_entity('CeleryTask', task_name=task_name)
    entity.cw_adapt_to('ICeleryTask').start(task, *args, **kwargs)
    return entity


def task_in_backend(task_id):
    app = celery.current_app
    if app.conf.CELERY_ALWAYS_EAGER:
        return False
    else:
        backend = app.backend
        return backend.get(backend.get_key_for_task(task_id)) is not None


class StartCeleryTaskOp(DataOperationMixIn, Operation):

    def postcommit_event(self):
        global _TEST_TASKS
        if self.cnx.vreg.config.mode == 'test':
            # In test mode, task should run explicitly with run_all_tasks()
            _TEST_TASKS.update(self.cnx.transaction_data.get('celerytask', {}))
        else:
            for eid in self.get_data():
                task = self.cnx.transaction_data.get('celerytask', {}).get(eid)
                if task is not None:
                    task.delay()


class CeleryTask(AnyEntity):
    __regid__ = 'CeleryTask'
    fetch_attrs, cw_fetch_order = fetch_config(('task_name',))

    def dc_title(self):
        return self.task_name

    def dc_long_title(self):
        adapted = self.cw_adapt_to('ICeleryTask')
        state, finished = adapted.state, adapted.finished
        title = self.task_name or self._cw._('subtask')
        if finished:
            title = '%s (%s)' % (title, self._cw._(state))
        return title

    @property
    def progress(self):
        yield self.cw_adapt_to('ICeleryTask').progress
        for subtask in self.reverse_parent_task:
            yield subtask.progress

    @property
    def parent_tasks(self):
        yield self
        for task in self.parent_task:
            for ptask in task.parent_tasks:
                yield ptask

    def child_tasks(self):
        yield self
        for task in self.reverse_parent_task:
            for ctask in task.child_tasks():
                yield ctask


class ICeleryTask(EntityAdapter):
    __regid__ = 'ICeleryTask'
    __abstract__ = True

    def start(self, name, *args, **kwargs):
        eid = self.entity.eid
        task = self.get_task(name, *args, **kwargs)
        self._cw.transaction_data.setdefault('celerytask', {})[eid] = task
        StartCeleryTaskOp.get_instance(self._cw).add_data(eid)

    def get_task(self, name, *args, **kwargs):
        """Should return a celery task / signature or None

        This method run in a precommit event
        """
        return celery.signature(name, args=args, kwargs=kwargs)

    def sync_state(self, task_id, task_name):
        """Triggered by celery-monitor"""
        raise NotImplementedError

    @property
    def task_id(self):
        raise NotImplementedError

    @property
    def task_name(self):
        raise NotImplementedError

    def revoke(self, terminate=True, signal='SIGKILL'):
        return celery.task.control.revoke(
            [self.task_id], terminate=terminate, signal=signal)

    @property
    def logs(self):
        return loghelper.get_task_logs(self.task_id) or b''

    @property
    def result(self):
        return AsyncResult(self.task_id)

    @property
    def progress(self):
        if celery.current_app.conf.CELERY_ALWAYS_EAGER:
            return 1.
        result = self.result
        if result.info and 'progress' in result.info:
            return result.info['progress']
        elif self.entity.reverse_parent_task:
            children = self.entity.reverse_parent_task
            return sum(child.cw_adapt_to('ICeleryTask').progress
                       for child in children) / len(children)
        elif result.state == STATES.SUCCESS:
            return 1.
        else:
            return 0.

    @property
    def state(self):
        return self.result.state

    @property
    def finished(self):
        return self.state in FINAL_STATES


def get_task_id(task):
    if hasattr(task, 'freeze'):
        # false for ASyncResult
        result = task.freeze()
    else:
        result = task
    if hasattr(result, 'task_id'):
        return result.task_id
    elif hasattr(result, 'id'):
        return result.id
    else:
        # Group
        return get_task_id(task.tasks[-1])


class CeleryTaskAdapter(ICeleryTask):
    """Base adapter that store task call args in the transaction"""

    __select__ = ICeleryTask.__select__ & is_instance('CeleryTask')

    def attach_task(self, task, seen, parent=None):
        task_id = six.text_type(get_task_id(task))
        if parent is None:
            parent = self.entity
        if self.entity.task_id is None:
            self.entity.cw_set(task_id=task_id)
        elif task_id not in seen:
            task_name = six.text_type(task.task)
            parent = self._cw.create_entity('CeleryTask',
                                            task_id=six.text_type(task_id),
                                            task_name=task_name,
                                            parent_task=parent)
        seen.add(task_id)
        if hasattr(task, 'body'):
            self.attach_task(task.body, seen, parent)
        if hasattr(task, 'tasks'):
            for subtask in task.tasks:
                self.attach_task(subtask, seen, parent)

    def get_task(self, name, *args, **kwargs):
        task = super(CeleryTaskAdapter, self).get_task(
            name, *args, **kwargs)
        self.attach_task(task, set())
        return task

    @property
    def task_id(self):
        return self.entity.task_id

    @property
    def task_name(self):
        return self.entity.task_name

    def revoke(self, terminate=True, signal='SIGKILL'):
        to_revoke = set([e.task_id for e in self.entity.child_tasks()])
        return celery.task.control.revoke(
            list(to_revoke), terminate=terminate, signal=signal)

    def attach_result(self, result):
        def tree(result, seen=None):
            if seen is None:
                seen = set()
            if result.parent:
                for r in tree(result.parent, seen):
                    yield r
            for child in result.children or []:
                for r in tree(child, seen):
                    yield r

            if isinstance(result, AsyncResult):
                rresult = result.result
                if (isinstance(rresult, dict)
                        and "celerytask_subtasks" in rresult):
                    subtasks = from_serializable(
                        rresult["celerytask_subtasks"])
                    for r in tree(subtasks, seen):
                        yield r

                if result.task_id not in seen:
                    seen.add(result.task_id)
                yield result

        for asr in tree(result):
            task_id = six.text_type(asr.id)
            try:
                cwtask = self._cw.find('CeleryTask', task_id=task_id).one()
            except NoResultError:
                cwtask = self._cw.create_entity(
                    'CeleryTask',
                    task_name=UNKNOWN_TASK_NAME,
                    task_id=six.text_type(task_id))
                self.info("Create <CeleryTask %s (task_id %s)>",
                          cwtask.eid, task_id)
            if not cwtask.parent_task and self.entity is not cwtask:
                self.info('Set %s parent_task to %s (%s)', cwtask.task_id,
                          self.entity, self.entity.task_id)
                cwtask.cw_set(parent_task=self.entity)

    def sync_state(self, task_id, task_name, commit=True):
        if (self.entity.task_name == UNKNOWN_TASK_NAME
                and task_name is not None):
            self.info('Update <CeleryTask %s (task_id %s)> name to %s',
                      self.entity.eid, task_id, task_name)
            self.entity.cw_set(task_name=six.text_type(task_name))

        result = self.result
        if result.ready():
            self.attach_result(result)

        transition = {
            STATES.SUCCESS: 'finish',
            STATES.FAILURE: 'fail',
            STATES.STARTED: 'start',
            STATES.REVOKED: 'fail',
            'PROGRESS': 'start',
        }.get(result.state)
        if transition is not None:
            self.info('<CeleryTask %s (task_id %s)> %s', self.entity.eid,
                      task_id, transition)
            wf = self.entity.cw_adapt_to('IWorkflowable')
            wf.fire_transition_if_possible(transition, result.traceback)
        else:
            self.info('<CeleryTask %s (task_id %s)> no transition found for '
                      'state %s', self.entity.eid, task_id, result.state)

        if commit:
            self._cw.commit()

    @property
    def logs(self):
        task_logs = self.entity.task_logs
        if task_logs is not None:
            task_logs.seek(0)
            return task_logs.read()
        else:
            return super(CeleryTaskAdapter, self).logs

    @property
    def state(self):
        db_state = self.entity.cw_adapt_to('IWorkflowable').state
        db_final_state_map = {'done': STATES.SUCCESS, 'failed': STATES.FAILURE}
        if db_state in db_final_state_map:
            return db_final_state_map[db_state]
        elif task_in_backend(self.task_id):
            return super(CeleryTaskAdapter, self).state
        return _('unknown state')
