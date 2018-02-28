from datetime import datetime
from bubot import BujectHelper
from bubot.BujectError import BujectError, SettingsError, UserError
from bson.objectid import ObjectId
from motor.motor_asyncio import AsyncIOMotorGridFS as GridFS
from bson.son import SON
import gridfs
from bubot.Action import Action
# import xmltodict
import glob
import base64
import copy


# os, fnmatch,


class Task:
    def __init__(self, db, **kwargs):
        self.data = {}
        #     '_id': None,
        #     # 'buject': None,
        #     'type': None,
        #     'subtype': None,
        #     'scenario_id': None,
        #     'number': None,
        #     'datetime': None,
        #     'name': None,
        #     'text': None,
        #     'object1': {},
        #     'object2': {},
        #     'object3': {},
        #     'object4': {},
        #     'owner': {},
        #     'role': {},
        #     'event': [],
        #     'file': [],
        #     'update': {
        #         'begin': None,
        #         'end': None,
        #     },
        #     'create': {
        #         'datetime': None
        #     },
        #     # 'last_change': None,
        # }
        # self.buject = buject
        # if buject:
        #     self.db = buject.db
        #     self.loop = buject.loop
        # else:
        self.db = db  # kwargs.get('db', None)
        self.loop = kwargs.get('loop', None)
        self.history = []
        self.events = []
        self.files = []
        self.event = []
        self.table = 'task'
        self.event_table = 'event'
        self.event_class = TaskEvent
        self.scenario = None
        self.file_class = TaskFile
        # if 'scenario_id' in kwargs:
        #     self.load_scenario(kwargs['scenario_id'])
        self.init()
        self.initialize(kwargs.get('data', None))
        # if 'data' in kwargs:
        #     self.data = BubotConfig.update_dict(self.data, kwargs['data'])

        # def _init(self):
        # super()._init()
        # if not self.db:
        #     self.get_db()

    def init(self):
        self.data = {
            '_id': None,
            'ext_id': None,
            # 'buject': None,
            'type': None,
            'subtype': None,
            'scenario_id': None,
            'scenario_name': None,
            'number': None,
            'datetime': None,
            'name': None,
            'text': None,
            'object1': {},
            'object2': {},
            'object3': {},
            'object4': {},
            'owner': {},
            'role': {},
            'events': [],
            'files': [],
            'update': {
                'begin': None,
                'end': None,
            },
            'create': {
                'datetime': None
            },
            # 'last_change': None,
        }
        self.events = []
        self.files = []
        self.history = []

    def initialize(self, data=None):
        self.data = BujectHelper.update_dict(self.data, data)
        if not self.data['_id']:
            self.data['_id'] = ObjectId()
        # if data:
        #     if 'task' in data and data['task']:
        #         self.data = BubotConfig.update_dict(self.data, data['task'])
        #     if 'events' in data and data['events']:
        #         self.events = data['events']
        #     if 'history' in data and data['history']:
        #         self.history = data['history']
        #     if 'files' in data and data['files']:
        #         self.files = data.pop('files']

    async def init_task(self, data):
        res = Action('ETask.init_task')
        self.init()
        new_task_data = data.get('task', {})
        new_event_data = data.get('event', {})
        new_files = data.get('files', [])
        if '_id' in new_task_data and new_task_data['_id']:  # ищем задачу
            if not self.find_by_id(ObjectId(new_task_data['_id'])):  # если указан ид, должна быть
                raise UserError('Задача не найдена', '_id: {0}'.format(new_task_data['_id']))
        elif 'ext_id' in new_task_data and new_task_data['ext_id']:
            await self.find_by_ext_id(new_task_data['ext_id'])
        if 'scenario_id' not in new_task_data or not new_task_data['scenario_id']:
            raise UserError('Не указан сценарий')
        changes = BujectHelper.compare_dict(self.data, new_task_data)
        self.initialize(new_task_data)
        await self.load_scenario()
        event_data = await self.get_active_stage(new_event_data.get('stage_id', None))
        self.event = self.event_class(self.db, data=event_data)
        self.event.initialize(new_event_data)
        if new_files:
            for file_data in new_files:
                file = self.file_class(self.db, data=file_data)
                await file.calc_file_param()
                self.event.upsert_file(file)
        # from file in self.event
        return res.set_end()
        pass

    async def find_one(self, query, projection=None):
        data = await self.db[self.table].find_one(query, projection)
        if data:
            self.init()
            self.initialize(data)
            return True
        return False


    async def find_by_id(self, _id):
        return await self.find_one({"_id": _id})

    async def find_by_ext_id(self, ext_id):
        return await self.find_one({"ext_id": ext_id})

    async def create_task(self, event, execute_action=True):
        try:
            # self.get_db()
            # self.load_scenario(event.data['scenario_id'])
            # event = TaskEvent(data=event_data, db=self.db, loop=self.loop)
            event.init()
            if '_id' not in event.data['task'] or not event.data['task']['_id']:
                event.data['task']['_id'] = ObjectId()
                self.data['_id'] = event.data['task']['_id']
            else:
                await self.load_task(event.data['task']['_id'], True)

            if not self.data['create']:
                self.data['create'] = datetime.now()
            if not self.data['datetime']:
                self.data['datetime'] = datetime.now()
            # self.data = BubotConfig.update_dict(self.data, data)
            # self.data = BubotConfig.update_dict(self.data, event_data['task'])

            # if not event.data['stage_id']:
            #     event.data['stage_id'] = await self.get_start_stage(event)

            if execute_action:
                if not event.data['action_id']:
                    stage = self.scenario.get_stage_by_id(event.data['stage_id'])
                    action = self.scenario.get_default_action(stage)
                    event.data['action_id'] = action['@id']
                event = await self.execute_action(self.data['_id'], event)
            else:
                await self.update_task_from_event(event)
                await self.save()
            return event

        except BujectError as e:
            raise BujectError(e, action_name='Task.create_task')
        except Exception as e:
            raise BujectError(e, action_name='Task.create_task')

    async def write(self, data):
        '''

        :param data:
        :return:
        '''
        res = Action('ETask.write')
        res.add_stat(await self.init_task(data))
        res.add_stat(await self.scenario.write_task(self))
        res.add_stat(await self.upsert_event(self.event))
        res.add_stat(await self.save())
        return res.set_end(self.data)
        pass

    async def prepare_action(self, data):
        '''

        :param data:
        :return:
        '''
        res = Action('Task.prepare_action')
        res.add_stat(await self.init_task(data))
        res.add_stat(await self.scenario.prepare_action(self))
        res.add_stat(await self.upsert_event(self.event))
        res.result = self.data
        res.result['event'] = self.event.data
        return res.set_end()
        pass

    async def execute_action(self, data):
        '''

        :param data:
        :return:
        '''
        res = Action('Task.execute_action')
        res.add_stat(await self.init_task(data))
        res.add_stat(await self.scenario.execute_action(self))
        res.add_stat(await self.upsert_event(self.event))
        return res.set_end(self.data)
        pass

    # async def _prepare_action(self, task_id, event):
    #     try:
    #         if not task_id:
    #             raise BujectError("Незаполнен обязательный параметр task_id", action_name='Task.prepare_action')
    #         # if not event.data['task'] or not event.data['task']['_id']:
    #         #     raise BujectError("Незаполнен обязательный параметр _id")
    #
    #         if self.data['_id'] != task_id:
    #             await self.load_task(event.data['task'], False)
    #         try:
    #             scenario_stage = self.scenario.get_stage_by_id(event.data['stage_id'])
    #             scenario_action = self.scenario.get_action_by_id(scenario_stage, event.data['action_id'])
    #         except KeyError:
    #             raise BujectError("Незаполнены обязательный параметры", action_name='Task.prepare_action')
    #         except Exception:
    #             raise BujectError("Незаполнены обязательный параметры", action_name='Task.prepare_action')
    #
    #         # if 'prepare_action' in scenario_action:
    #         #     for handler in scenario_action['prepare_action']:
    #         #         temp_event = getattr(self, handler)(scenario_stage, scenario_action, event)
    #         #         if temp_event:
    #         #             event.data = BubotConfig.update_dict(event.data, temp_event)
    #         #
    #         # for next_stage_name in scenario_action['next_stage']:
    #         #     await self.stage_incoming_check(next_stage_name, event)
    #
    #         return event
    #
    #     except BujectError as e:
    #         raise BujectError(e,
    #                           action_name='Task.prepare_action',
    #                           action_param={
    #                               'stage_id': event.data['stage_id'],
    #                               'action_id': event.data['action_id']
    #                           })
    #     except Exception as e:
    #         raise BujectError(e)
    #
    # async def _execute_action(self, task_id, event):
    #     if not task_id:
    #         raise BujectError("Незаполнен обязательный параметр task_id", action_name='Task.execute_action')
    #
    #     if self.data['_id'] != task_id:
    #         await self.load_task(task_id, True)
    #     try:
    #         event_data = event.data
    #         scenario_stage = self.scenario.get_stage_by_id(event_data['stage_id'])
    #         scenario_action = self.scenario.get_action_by_id(scenario_stage, event_data['action_id'])
    #     except KeyError:
    #         raise BujectError("Незаполнены обязательные параметры", action_name='Task.execute_action')
    #
    #     except BujectError as e:
    #         raise BujectError(e, action_name='Task.execute_action')
    #
    #     except Exception:
    #         raise BujectError("Незаполнены обязательные параметры", action_name='Task.execute_action')
    #
    #     try:
    #         event = await self.prepare_action(task_id, event)
    #         # if 'execute_action' in scenario_action:
    #         #     for handler in scenario_action['execute_action']:
    #         #         try:
    #         #             temp_result = await getattr(self, handler)(scenario_stage, scenario_action, event)
    #         #             if temp_result:
    #         #                 event.data = BubotConfig.update_dict(event.data, temp_result)
    #         #         except Exception as e:
    #         #             raise BujectError("Неизвестная ошибка" % str(e))
    #
    #         if not self.data['_id']:
    #             event.data['task']['_id'] = ObjectId()  # хз что это
    #
    #         next_stages = self.scenario.get_next_stages(scenario_stage, scenario_action)
    #         for next_stage in next_stages['stage']:
    #             new_event = await self.create_stage(next_stage, event)
    #             if new_event:
    #                 self.data['event'].append(new_event.data)
    #                 # if self.update_stage(new_event.data['stage_id']):  # обновляем статус
    #                 #     event.data['task']['stage_id'] = new_event.data['stage_id']
    #                 # await new_event.save()
    #
    #         self.data = BubotConfig.update_dict(self.data, event.data['task'])
    #
    #         # self.data['file'] = BubotConfig.update_dict(self.data['file'], event.data['file'])
    #         # # переносим вложения
    #         # for event_file in event_data['file']:
    #         #     find_division = False
    #         #     i = 0
    #         #     for task_file in self.data['file']:
    #         #         if task_file['ext_id'] == event_file['ext_id']:
    #         #             self.data['file'][i] = BubotConfig.update_dict(task_file, event_file)
    #         #             find_division = True
    #         #             break
    #         #         i += 1
    #         #     if not find_division:
    #         #         self.data['file'].append(event_file)
    #         # # очищаем статус
    #         event.close()
    #         await self.update_task_from_event(event)
    #
    #         await self.save()
    #         self.data['status_id'] = 200
    #
    #         # await event.save()
    #         return event
    #     except BujectError as e:
    #         raise BujectError(e, action_name='Task.execute_action',
    #                           action_param=event_data)
    #     except Exception as e:
    #         raise BujectError(e)

    # async def update_task_from_event(self, event):
    #     event_id = str(event.data['_id'])
    #     update = False
    #     for task_event in self.data['event']:
    #         if str(task_event['_id']) == event_id:
    #             BubotConfig.update_dict(task_event, event.data)
    #             update = True
    #             break
    #     if not update:
    #         self.data['event'].append(event.data)
    #
    #     BubotConfig.update_dict(self.data, event.data['task'])
    #
    #     for file_data in event.data['file']:
    #         # загружаем вложения
    #         content = file_data.pop('content', None)
    #         if content:
    #             file = self.file_class(self.db, data=file_data)
    #             if 'binary' in content:
    #                 await file.save_file_data(content['binary'], self, event)
    #         # обновляем инфу о файлах на задаче
    #         add = False
    #         task_file = file_data
    #         task_file['create'] = event.data['datetime']
    #         # {
    #         #     'name': file_data['name'],
    #         #     'file_name': file_data['file_name'],
    #         #     'role': file_data['role'],
    #         #     'content_type': file_data['content_type'],
    #         # }
    #         if 'file' in self.data:
    #             for i, file in enumerate(self.data['file']):
    #                 if file['file_name'] == file_data['file_name'] and \
    #                         (not file['create'] or file['create'] < event.data['datetime']):
    #                     self.data['file'][i] = task_file
    #                     add = True
    #         else:
    #             self.data['file'] = []
    #         if not add:
    #             self.data['file'].append(task_file)
    #
    # async def load_task(self, task_id, lock):
    #     try:
    #         # self.get_db()
    #         # task_id = ObjectId(task_data['_id'])
    #         if lock:
    #             result = await self.db.command(
    #                 SON([("findAndModify", self.table),
    #                      ("query", {'_id': task_id}),
    #                      ("update", {'$set': {'status_id': 301}}),
    #                      ("new", True)
    #                      ]))
    #             self.data = result['value']
    #
    #         else:
    #             self.data = await self.db[self.table].find_one({'_id': task_id})
    #         if not self.data:
    #             raise BujectError("task not found", action_param=task_id, action_name='Task.load_task')
    #         await self.load_scenario(self.data['scenario_id'])
    #
    #     except BujectError as e:
    #         raise BujectError(e, action_name='Task.load_task')
    #     except Exception as e:
    #         raise BujectError(e, action_name='Task.load_task')

    # def update_stage(self, new_stage):
    #     try:
    #         if not self.data['stage_id']:
    #             return True
    #         try:
    #             current_scenario_stage = self.scenario.get_stage_by_id(self.data['stage_id'])
    #         except BujectError:  # стадии в регламенте уже нет, вероятно переименовали.
    #             current_scenario_stage = {'order': 1}
    #
    #         new_scenario_stage = self.scenario.get_stage_by_id(new_stage)
    #         if current_scenario_stage['order'] < new_scenario_stage['order']:
    #             return True
    #         return False
    #     except BujectError as e:
    #         raise BujectError(e, action_name='Task.update_stage')
    #     except Exception as e:
    #         raise BujectError(e, action_name='Task.update_stage')
    #
    # async def stage_incoming_check(self, stage_name, event):
    #     try:
    #         stage = self.scenario.get_stage_by_id(stage_name)
    #         if 'stage_incoming_check' in stage:
    #             for handler in stage['stage_incoming_check']:
    #                 await getattr(self, handler)(stage_name, event)
    #     except BujectError as e:
    #         raise BujectError(e, action_name='Task.stage_incoming_check', action_param=stage_name)
    #     except Exception as e:
    #         raise BujectError(e, action_name='Task.stage_incoming_check', action_param=stage_name)
    #
    #
    # async def get_start_stage(self, event):
    #     # возвращаем первую попавшуюся стартовую стадию которая может запуститься
    #     for stage_name in self.scenario.data['stage']:
    #         stage = self.scenario.get_stage_by_id(stage_name)
    #         if 'start' not in stage or not stage['start']:
    #             continue
    #         try:
    #             await self.stage_incoming_check(stage_name, event)
    #         except BujectError:
    #             continue
    #         return stage_name
    #     raise BujectError("Нет ни одного доступного стартового этапа")

    def check_action(self, stage_id, action_id=None):
        if not self.scenario:
            self.load_scenario(self.data['scenario_id'])
        try:
            stage = self.scenario.get_stage_by_id(stage_id)
        except BujectError:
            raise BujectError("Неподдерживаемое событие", stage_id,
                              action_name='Task.check_action')

        # если указан переход проверяем доступен ли он на регламете, если переход не указан явно берем первый
        if action_id:
            if not self.scenario.get_action_by_id(stage, action_id):
                raise BujectError("Неподдерживаемый переход", action_id,
                                  action_name='Task.check_action')
        else:
            action = self.scenario.get_default_action(stage)
            action_id = action['@id']

        return action_id

    async def create_stage(self, stage):
        '''

        :param stage:
        :param current_event:
        :return:
        '''
        try:
            res = Action('Task.create_stage')
            # проверяем , не создавали ли мы уже следующие этапы ранее.
            event_data = {}

            match = 0
            for temp_event in self.data['events']:
                if temp_event["stage_id"] == stage['@id'] and (
                                temp_event["parent"] is None or temp_event['parent'] == self.event.data['_id']):
                    event_data = temp_event
                    match += 1

            # event_data = await event.find_one({
            #     'task._id': event.data['task']['_id'],
            #     'stage_id': stage['@id'],
            #     '$or': [{'parent_id': None}, {'parent_id': event.data['_id']}]
            # })
            # if match == 0:
            #     event_data = {}
            # if match == 1:  # событие уже есть ничего создавать не надо
            #     return res.set_end(None)
            if match > 1:
                raise BujectError('create_stage найдено несколько созданных этапов')
            event_data['parent'] = self.event.data['_id']
            event_data['stage_datetime'] = self.event.data['action_datetime']
            event_data['stage_id'] = stage['@id']

            new_event = self.event_class(self.db, data=event_data)
            res.add_stat(await self.scenario.create_stage(self, new_event))
            return res.set_end(new_event)
        except BujectError as e:
            raise BujectError(e, action_name='Task.create_stage', action_param=stage['@id'])
        except Exception as e:
            raise BujectError(e)

    async def load_scenario(self, scenario_key=None):
        scenario = TaskScenario(self.db)
        key = scenario_key if scenario_key else self.data['scenario_id']
        if not key:
            raise UserError('Не указан сценарий')

        if await scenario.find_by_key(key):
            self.scenario = scenario
            self.data['scenario_name'] = scenario.data['name']
        else:
            raise UserError('Не найден сценарий {0}'.format(key))

    async def get_begin_stage(self):
        _stages = self.scenario.get_begin_stages()
        if _stages:
            stages = []
            for elem in _stages:
                # event = self.event_class(self.db, data=)
                stages.append({
                    'stage_id': elem['@id']
                })
            return stages
        else:
            raise SettingsError('Нет доступных стартовых этапов')

    async def get_active_stage(self, stage_id=None):
        stages = await self.get_active_stages()
        if stage_id:
            for stage_data in stages:
                if stage_id == stage_data['stage_id']:
                    return stage_data
            raise UserError('Не найден активный этап "{0}"'.format(stage_id))

        size = len(stages)
        if size == 1:
            return stages[0]
        elif size > 1:
            raise UserError('Несколько активных стадий', str(stages))
        else:
            raise SettingsError('Не найдено активного этапа')

    async def get_active_stages(self):
        stages = []
        if not self.data['events']:
            stages = await self.get_begin_stage()
        else:
            for event in self.data['events']:
                if event['stage_id'] and event['action_id'] is None:
                    stages.append(event)
        return stages

    async def get_available_actions(self, types, user):
        available_actions = []
        # if not self.events:
        #     self.scenario.
        #     pass

        for event in self.data['event']:
            if event['action_id'] is not None:
                continue
            scenario_stage = self.scenario.get_stage_by_id(event['stage_id'])
            if scenario_stage['@bpmn_type'] not in types:
                continue
            default_action = scenario_stage.get('@default', None)
            scenario_action = self.scenario.get_available_actions(scenario_stage)
            for action in scenario_action:
                data = {
                    'stage_id': event['stage_id'],
                    'action_id': action['@id'],
                    'action_name': action['@name']
                }
                if default_action and action['@id'] == default_action:
                    available_actions.insert(0, data)
                else:
                    available_actions.append(data)
        return available_actions

    def upsert_file_to_task(self, file):
        try:
            add = False
            task_file = {
                'name': file.data['name'],
                'file_name': file.data['file_name'],
                'role': file.data['role'],
                'type': file.data['type'],
            }
            for file in self.data['files']:
                if task_file['file_name'] == file['file_name']:
                    file = task_file
                    add = True
            if not add:
                self.data['files'].append(task_file)
        except BujectError as e:
            raise BujectError(e, action_name='add_file_to_task')
        except Exception as e:
            raise BujectError(e)

    async def upsert_event(self, event):
        res = Action('Task.upsert_event')
        if not event:
            return res
        if event.data['files']:
            for file_data in event.data['files']:
                file = self.file_class(self.db, data=file_data, loop=self.loop)
                binary = file_data.pop('binary', None)
                if binary:
                    binary = base64.b64decode(binary)
                    res.add_stat(await file.upsert(binary, self))
                    self.upsert_file_to_task(file)

        add = True

        for elem in self.data['events']:
            if elem['_id'] == event.data['_id']:
                elem = event.data
                add = False
                break
        if add:
            self.data['events'].append(event.data)

        return res.set_end()
        pass

    async def save(self):
        res = Action('Task.save')
        return res.set_end(await self.db[self.table].save(self.data))


class TaskScenario:
    def __init__(self, db, **kwargs):
        self.db = db
        self.table = 'scenario'
        self.data = {}
        self.handler = None
        self.initialize(kwargs.get('data', None))

    def initialize(self, data):
        if data:
            self.data = BujectHelper.update_dict(self.data, data)
        try:
            if self.data.get('handler', None):
                self.handler = BujectHelper.get_class(self.data['handler'])
                self.handler = self.handler(self.db)
        except Exception:
            pass

    async def find_by_key(self, key):
        data = await self.db[self.table].find_one({'key': key})
        if data:
            self.initialize(data)
            return True
        return False

    @staticmethod
    def get_stage_type(stage):
        return stage['@bpmn_type'][0:-4].lower()

    def get_stage_by_id(self, stage_id):
        try:
            stage = self.data['process'][stage_id]
            if stage['@bpmn_type'][-4:].lower() == 'task':
                return stage
        except Exception:
            raise BujectError('Stage not found {0}'.format(stage_id),
                              action_name='TaskScenario.get_stage_by_id')
        raise BujectError('Stage not found {0}'.format(stage_id),
                          action_name='TaskScenario.get_stage_by_id')

    def get_action_by_id(self, stage, action_id):
        try:
            action = self.data['process'][action_id]
            if action['@bpmn_type'] == 'sequenceFlow' and action['@sourceRef'] == stage['@id']:  # возможно это gateway
                return action
        except Exception:
            raise BujectError('Action not found', action_id)

        raise BujectError('Action not found', action_id,
                          action_name='TaskScenario.get_stage_by_id')

    def get_available_actions(self, stage):
        try:
            action_links = stage['bpmn2:outgoing']
            action = []
            if isinstance(action_links, str):
                action_links = [action_links, ]
            for action_id in action_links:
                try:
                    action.append(self.get_action_by_id(stage, action_id))
                except:
                    continue
            return action
        except Exception:
            raise BujectError('Default action not found')

    def get_default_action(self, stage):
        try:
            if '@default' in stage:
                action_id = stage['@default']
            elif isinstance(stage['bpmn2:outgoing'], str):
                action_id = stage['bpmn2:outgoing']
            else:
                raise BujectError('Default action not found', action_name='TaskScenario.get_default_action')

            return self.get_action_by_id(stage, action_id)
        except Exception:
            raise BujectError('Default action not found', action_name='TaskScenario.get_default_action')

    def get_begin_stages(self):
        stages = []
        for key in self.data['process']:
            stage = self.data['process'][key]
            if stage['@bpmn_type'] != 'startEvent':
                continue
            action = self.data['process'][stage['bpmn2:outgoing']]
            stages.extend(self.get_next_stages(stage, action))
        return stages

    def get_next_stages(self, stage, action):
        try:
            def end_event(_self, _next_stage):
                next_stages.append(_next_stage)
                return

            # def event(_self, _next_stage):
            #     _actions = _self.get_available_actions(_next_stage)
            #     next_stages['prepare'].append(_next_stage)
            #     for _action in _actions:
            #         check_next_stage(_next_stage, _action)
            #     pass

            def parallel_gateway(_self, _next_stage):
                _actions = _self.get_available_actions(_next_stage)
                for _action in _actions:
                    check_next_stage(_next_stage, _action)
                pass

            def task(_self, _next_stage):
                next_stages.append(_next_stage)
                return

            def check_next_stage(_stage, _action):

                next_stage = self.data['process'][_action['@targetRef']]
                if next_stage['@bpmn_type'] in handler:
                    handler[next_stage['@bpmn_type']](self, next_stage)
                else:
                    raise BujectError("Неподдерживаемый объект BPMN", next_stage['@bpmn_type'])

            next_stages = []
            handler = {
                'parallelGateway': parallel_gateway,
                'endEvent': end_event,
                'sendTask': task,
                'receiveTask': task,
                'serviceTask': task,
                'task': task,
                'userTask': task,
                # 'intermediateThrowEvent': event,
                # 'intermediateCatchEvent': event
            }
            check_next_stage(stage, action)
            return next_stages
        except Exception as e:
            raise BujectError("Неподдерживаемый объект BPMN")

    async def import_bpmn(self, path='./*.bpmn'):
        list_scenario = {}
        list = glob.glob(path)
        for file_name in list:
            with open(file_name, encoding='utf-8') as fd:
                doc = xmltodict.parse(fd.read())
                scenario = TaskScenario(self.db)
                scenario.parse_bpmn(doc)
                await scenario.save()
        return list_scenario

    def parse_bpmn(self, source):

        process = {}
        try:
            source = source['bpmn2:definitions']['bpmn2:process']
        except Exception:
            return
        self.data = {
            'key': source['@id'],
            'name': source['@name'],
            'process': process
        }
        for elem1 in source:
            if elem1[0:4] != 'bpmn':
                continue
            bpmn_type = elem1[6:]

            if isinstance(source[elem1], list):
                for elem2 in source[elem1]:
                    elem2['@bpmn_type'] = bpmn_type
                    process[elem2['@id']] = elem2
            else:
                source[elem1]['@bpmn_type'] = bpmn_type
                process[source[elem1]['@id']] = source[elem1]

    async def write_task(self, task):
        res = Action()
        if self.handler:
            res.set_end(res.add_stat(await self.handler.write_task(task)))
        return res
        pass

    async def create_stage(self, task, new_event):
        res = Action()
        if self.handler:
            res.set_end(res.add_stat(await self.handler.create_stage(task, new_event)))
        return res

    async def prepare_action(self, task):
        res = Action()
        if self.handler:
            res.set_end(res.add_stat(await self.handler.prepare_action(task)))
        return res

    async def execute_action(self, task):
        res = Action()
        scenario_stage = self.get_stage_by_id(task.event.data['stage_id'])
        scenario_action = self.get_action_by_id(scenario_stage, task.event.data['action_id'])

        next_stages = self.get_next_stages(scenario_stage, scenario_action)
        for next_stage in next_stages['stage']:
            new_event = res.add_stat(await task.create_new_stage(next_stage))
            res.add_stat(await task.upsert_event(new_event))

        if not self.handler:
            res.add_stat(await self.handler.execute_action(task))
        return res.set_end()
        pass

    async def save(self):
        await self.db[self.table].update_one({'key': self.data['key']}, {'$set': self.data}, upsert=True)


class TaskScenarioHandler:
    def __init__(self, db):
        self.db = db

    async def write_task(self, task):
        pass

    async def create_stage(self, task, new_event):
        pass

    async def prepare_action(self, task):
        pass

    async def execute_action(self, task):
        pass


class TaskAction:
    def __init__(self, data=None):
        self.data = {
            "id": None,
            "name": None,
            'datetime': None,
            'object1': {},
        }
        # self.scenario = scenario
        if data:
            self.data = BujectHelper.update_dict(self.data, data)

    def create_new_stage(self, stage_name, event):
        # event = BujectTaskEvent(event)
        stage = event.scenario.get_stage_by_id(stage_name)
        if 'create_handler' in stage:
            for handler in stage['create_handler']:
                temp_result = getattr(self, handler)(stage_name, event)
                if temp_result:
                    self.data = BujectHelper.update_dict(event.data, temp_result)
        event.data['stage']['id'] = stage_name
        if not event.data['create']:
            event.data['create'] = datetime.now()
        # event.data['_id'] = self.loop.run_until_complete(self.db.event.save(event.data))
        return event.data


class TaskStage:
    def __init__(self, data=None):
        self.data = {
            "id": None,
            "name": None,
            'object1': {},
        }
        # self.scenario = scenario
        if data:
            self.data = BujectHelper.update_dict(self.data, data)

    def init(self, event):
        stage_name = self.data["name"]
        stage = event.scenario.get_stage_by_id(stage_name)
        if 'create_handler' in stage:
            for handler in stage['create_handler']:
                temp_result = getattr(self, handler)(stage_name, event)
                if temp_result:
                    self.data = BujectHelper.update_dict(event.data, temp_result)


class TaskEvent:
    def __init__(self, db, **kwargs):
        self.data = {}
        self.task_table = 'task'
        # self.table = 'task_event'
        self.db = db
        self.task = kwargs.get('task', None)
        self.init()
        self.initialize(kwargs.get('data', None))

    def init(self):
        self.data = {
            '_id': None,
            'parent': None,
            'ext_id': None,
            # 'task_ref': None,
            # 'buject': None,
            'text': None,
            # 'action': TaskAction().data,
            # 'stage': TaskStage().data,
            # 'status': {},
            'files': [],
            'param': {},
            'task': {},
            'stage_id': None,
            'stage_type': None,
            'stage_performer_ref': None,
            'stage_datetime': None,
            'stage_deadline': None,
            'action_id': None,
            'action_performer_ref': None,
            'action_datetime': None,
            'action_status_id': None,
            'action_status_msg': None,
            'action_status_datetime': None,
            # 'scenario_id': None,
            'datetime': None,
            'processed': None
        }

    def initialize(self, data):
        self.data = BujectHelper.update_dict(self.data, data)
        # if 'files' in data:
        #     for file_data in data['files']:
        #         file = TaskFile(self.db, data=file_data)
        #         self.upsert_file(file)
        if not self.data['_id']:
            self.data['_id'] = ObjectId()
        pass

    def upsert_file(self, new_file):
        try:
            add = False
            for file in self.data['files']:
                if file['ext_id'] and file['ext_id'] == new_file.data['ext_id']:
                    file = new_file.data
                    add = True
            if not add:
                self.data['files'].append(new_file.data)
        except BujectError as e:
            raise BujectError(e, action_name='uosert_file')
        except Exception as e:
            raise BujectError(e)

    async def save_files(self):
        pass

    # async def find_one(self, query, projection=None):
    #     return await self.db[self.table].find_one(query, projection)

    def close(self):
        self.data['processed'] = datetime.now()
        self.data['status_datetime'] = datetime.now()
        self.data['status_id'] = 200

        # async def save(self):
        #     result = await self.db[self.table].save(self.data)
        #     # return result


# class TaskIntEvent:
#     def __init__(self, db, **kwargs):
#         self.data = {
#             '_id': None,
#             'task_ref': None,
#             'buject': None,
#             'text': None,
#             'file': [],
#             'data': {},
#             'task': {},
#             'stage_id': None,
#             'stage_performer_ref': None,
#             'stage_datetime': None,
#             'stage_deadline': None,
#             'action_id': None,
#             'action_performer_ref': None,
#             'action_datetime': None,
#             'action_status_id': None,
#             'action_status_msg': None,
#             'action_status_datetime': None,
#             'organization': None,
#             # 'scenario_id': None,
#             'datetime': None,
#             'create': None,
#             'processed': None
#         }
#         # self.buject = buject
#         self.task_table = 'task'
#         self.table = 'task_event'
#         self.db = db
#
#         if not self.db:
#             raise BujectError('In buject {0} not initialized DB'.format(buject.id))
#
#         self.loop = buject.loop
#         # self.scenario = scenario
#         if 'data' in kwargs:
#             # self.data = BubotConfig.update_dict(self.data, kwargs['data'])


class TaskFile:
    def __init__(self, db, **kwargs):
        self.data = {}
        self.task_table = 'task'
        self.db = db
        self.init()
        self.initialize(kwargs.get('data', None))

    def init(self):
        self.data = {
            '_id': '',
            'type': None,
            'name': None,
            'file_name': None,
            'parent': None,
            'ext_id': None,
            'role': None,
            'format_name': None,
            'format_version': None,
        }

    def initialize(self, data):
        try:
            self.data['file_name'] = data['file_name']
            self.data['name'] = data.get('name', self.data['name'] if self.data['name'] else data['file_name'])
            self.data['parent'] = data.get('parent', self.data['parent'])
            self.data['ext_id'] = data.get('ext_id', self.data['ext_id'])
            if 'binary' in data and data['binary']:
                self.data['binary'] = data['binary']

            if not self.data['_id']:
                self.data['_id'] = ObjectId()
        except KeyError as e:
            raise UserError('Не указан обязательный параметр {0}'.format(str(e)))

    async def find_by_ext_id(self, task_ext_id, event_ext_id, ext_id):
        return await self.db['{0}.files'.format(self.task_table)].find_one({'$and': [
            {'task_ext_id': task_ext_id},
            {'event_ext_id': event_ext_id},
            {'ext_id': ext_id}
        ]})

    async def find_by_id(self, _id):
        return await self.db['{0}.files'.format(self.task_table)].find_one({'_id': _id})

    # def close(self):
    #     self.data['processed'] = datetime.now()
    #     self.data['status_id'] = 200

    # async def save(self):
    #     result = await self.db['{0}_file'.format(self.task_table)].save(self.data)
    #     return
    async def upsert(self, binary, task):
        res = Action('TaskFile.upsert')
        try:
            if res.add_stat(await self.exists_file_data()):
                res.add_stat(await self.delete_file_data())
            res.add_stat(await self.save_file_data(binary, task))
            return res.set_end()
        except BujectError as e:
            raise BujectError(e, action=res)
        except Exception as e:
            raise BujectError(e, action=res)

    async def save_file_data(self, data, task):
        res = Action('TaskFile.save_file_data')
        try:
            fs = GridFS(self.db, self.task_table)
            param = {
                '_id': self.data['_id'],
                'filename': self.data['file_name'],
                'contentType': self.get_mime_type_by_file_name(self.data['file_name']),
                'name': self.data['name'],
                'format_name': self.data['format_name'],
                'format_version': self.data['format_version'],
                'task_ext_id': task.data['ext_id'],
                'event_ext_id': task.event.data['ext_id'],
                'ext_id': self.data['ext_id'],
                'task_id': task.data['_id'],
                'event_id': task.event.data['_id']
            }
            f = await fs.new_file(**param)
            try:
                await f.write(data)
            finally:
                await f.close()
        # except gridfs.errors.FileExists:
        #     return
        except Exception as e:
            raise BujectError(e, 'save_file_data')
        return res.set_end()

    async def delete_file_data(self):
        res = Action('TaskFile.delete_file_data')
        try:
            fs = GridFS(self.db, self.task_table)
            await fs.delete(self.data['_id'])
            return res.set_end()
        except Exception as e:
            raise BujectError(e, 'delete_file_data')

    async def exists_file_data(self):
        res = Action('TaskFile.exists_file_data')
        try:
            fs = GridFS(self.db, self.task_table)
            return res.set_end(await fs.exists(self.data['_id']))
        except Exception as e:
            raise BujectError(e, 'delete_file_data')

    async def get_file_data(self):
        try:
            fs = GridFS(self.db, self.task_table)
            try:
                f = await fs.get(self.data['_id'])
            except gridfs.NoFile:
                raise BujectError("file not found")
            return await f.read()
        except Exception as e:
            raise BujectError(e, 'get_file_data')

    @staticmethod
    def get_mime_type(self, name):
        ext = {
            'xml': 'text/xml',
            'p7s': 'application/x-pkcs7-signature',
            'sig': 'application/x-pkcs7-signature',
            'pdf': 'application/pdf',
        }
        try:
            return ext[name.rfind]
        except KeyError:
            return 'nonformalized'

    @staticmethod
    def get_content_type_by_file_name(file_name,):
        available_type = {
            '': ('bin', ''),  # code, mime
            'xml': ('xml', 'text/xml'),
            'p7s': ('sig', 'application/x-pkcs7-signature'),
            'sig': ('sig', 'application/x-pkcs7-signature')
        }
        ext_delimiter = file_name.rfind('.')
        if ext_delimiter == -1:
            return available_type[''][0]
        ext = file_name[ext_delimiter + 1:]
        try:
            return available_type[ext][0]
        except KeyError:
            return available_type[''][0]

    @staticmethod
    def get_mime_type_by_file_name(file_name, ):
        available_type = {
            '': ('bin', ''),  # code, mime
            'xml': ('xml', 'text/xml'),
            'p7s': ('sig', 'application/x-pkcs7-signature'),
            'sig': ('sig', 'application/x-pkcs7-signature')
        }
        ext_delimiter = file_name.rfind('.')
        if ext_delimiter == -1:
            return available_type[''][1]
        ext = file_name[ext_delimiter + 1:]
        try:
            return available_type[ext][1]
        except KeyError:
            return available_type[''][1]

    async def calc_file_param(self):
        pass

if __name__ == '__main__':
    pass
