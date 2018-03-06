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

"""cubicweb-celerytask specific hooks and operations"""
from __future__ import print_function

from celery import current_app
import celery.task.control

from cubicweb import Binary
from cubicweb.predicates import on_fire_transition, is_instance
from cubicweb.server.hook import Hook, DataOperationMixIn, Operation

from cw_celerytask_helpers.redislogger import flush_task_logs


class FlushCeleryTaskLogsOp(DataOperationMixIn, Operation):

    def postcommit_event(self):
        for task_id in self.get_data():
            flush_task_logs(task_id)


class CeleryTaskFinishedHook(Hook):
    __regid__ = 'celerytask.celerytask_finished'
    __select__ = (Hook.__select__ &
                  on_fire_transition('CeleryTask', ('finish', 'fail')))
    events = ('after_add_entity',)

    def __call__(self):
        if current_app.conf.CELERY_ALWAYS_EAGER:
            return
        entity = self.entity.for_entity
        logs = Binary(entity.cw_adapt_to('ICeleryTask').logs)
        entity.cw_set(task_logs=logs)
        FlushCeleryTaskLogsOp.get_instance(self._cw).add_data(entity.task_id)


class DeleteCeleryTaskOp(DataOperationMixIn, Operation):

    def postcommit_event(self):
        tasks = set(self.get_data())
        if tasks:
            celery.task.control.revoke(list(tasks), terminate=True,
                                       signal='SIGKILL')
        for task_id in tasks:
            flush_task_logs(task_id)


class CeleryTaskDeletedHook(Hook):
    """revoke task and flush task logs when a task is deleted"""
    __regid__ = 'celerytask.celerytask_deleted'
    __select__ = Hook.__select__ & is_instance('CeleryTask')
    events = ('after_delete_entity',)

    def __call__(self):
        op = DeleteCeleryTaskOp.get_instance(self._cw)
        for task in self.entity.child_tasks():
            op.add_data(task.task_id)
