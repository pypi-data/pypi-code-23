import datetime
import time
import copy

from open_publishing.core.enums import EventTarget, EventAction, EventType

class Events(object):
    def __init__(self,
                 ctx):
        self._ctx = ctx

    def all_events(self,
                   references = None,
                   target = None,
                   action = None,
                   type = None,
                   filters = None,
                   since = None,
                   till = None):
        event_types = self._get_event_types(target,
                                            action,
                                            type,
                                            filters)
        
        if references is None:
            pass
        elif isinstance(references, (list, tuple)):
            references = ','.join(references)
        else:
            raise TypeError('references: expected list or tuple, got: {0}'.format(type(references)))

        if isinstance(since, (datetime.datetime, datetime.date)):
            from_timestamp = int(time.mktime(since.timetuple()))
        elif since is None:
            from_timestamp = None
        else :
            raise TypeError('since should be datetime.datetime or datetime.date, got {0}'.format(since))

        if isinstance(till, (datetime.datetime, datetime.date)):
            to_timestamp = int(time.mktime(till.timetuple()))
        elif till is None:
            to_timestamp = None
        else :
            raise TypeError('till should be datetime.datetime or datetime.date, got {0}'.format(till))




        response = self._ctx.gjp.fetch_events(method='list_status',
                                              event_types=event_types,
                                              references=references,
                                              from_timestamp=from_timestamp,
                                              to_timestamp=to_timestamp)

        execution_timestamp = datetime.datetime.fromtimestamp(response['execution_timestamp'])
        result = EventsList(execution_timestamp)

        def add_items(items):
            for item in items:
                result.append(EventsList.Event(target = EventTarget.from_id(item['target']),
                                               action = EventAction.from_id(item['action']),
                                               type = EventType.from_id(item['type']),
                                               timestamp = datetime.datetime.fromtimestamp(item['last_modified']),
                                               guid = (item['source_type'] + '.' + str(item['reference_id'])).lower()))

        add_items(response['items'])
        while 'resumption_token' in response:
            response = self._ctx.gjp.fetch_events('list_status',
                                                  resumption_token=response['resumption_token'])
            add_items(response['items'])

        result.sort(key=lambda a: a.timestamp)
        return result

    def last_event(self,
                   references,
                   target = None,
                   action = None,
                   type = None,
                   filters = None):
        event_types = self._get_event_types(target,
                                            action,
                                            type,
                                            filters)
        
        if isinstance(references, (list, tuple)):
            str_references = ','.join(set(references))
        else:
            raise TypeError('references: expected list or tuple, got: {0}'.format(type(references)))

        events = {}
        def add_items(items):
            for item in items:
                guid = (item['source_type'] + '.' + str(item['reference_id'])).lower()
                if guid not in events or events[guid]['last_modified'] < item['last_modified']:
                    events[guid] = item


        response = self._ctx.gjp.fetch_events(method='list_status',
                                              event_types=event_types,
                                              references=str_references)

        execution_timestamp = datetime.datetime.fromtimestamp(response['execution_timestamp'])

        add_items(response['items'])
        while 'resumption_token' in response:
            response = self._ctx.gjp.fetch_events('list_status',
                                                  resumption_token=response['resumption_token'])
            add_items(response['items'])

        result = EventsList(execution_timestamp)
        for ref in references:
            guid = ref.lower()
            if guid in events:
                result.append(EventsList.Event(target = EventTarget.from_id(events[guid]['target']),
                                               action = EventAction.from_id(events[guid]['action']),
                                               type = EventType.from_id(events[guid]['type']),
                                               timestamp = datetime.datetime.fromtimestamp(events[guid]['last_modified']),
                                               guid = guid))
            else:
                result.append(None)
        return result



    def fetch(self,
              target = None,
              action = None,
              type = None,
              filters = None,
              references = None,
              since = None,
              till = None):
        return self._fetch(target=target,
                           action=action,
                           type=type,
                           filters=filters,
                           references=references,
                           since=since,
                           till=till,
                           guid_filter=lambda guid: (guid.startswith('document.') or
                                                     guid.startswith('user.') or
                                                     guid.startswith('account.')))

    def fetch_documents(self,
                        target = None,
                        action = None,
                        type = None,
                        filters = None,
                        references = None,
                        since = None,
                        till = None):
        return self._fetch(target=target,
                           action=action,
                           type=type,
                           filters=filters,
                           references=references,
                           since=since,
                           till=till,
                           guid_filter=lambda guid: guid.startswith('document.'))

    def fetch_users(self,
                    target = None,
                    action = None,
                    type = None,
                    filters = None,
                    references = None,
                    since = None,
                    till = None):
        return self._fetch(target=target,
                           action=action,
                           type=type,
                           filters=filters,
                           references=references,
                           since=since,
                           till=till,
                           guid_filter=lambda guid: guid.startswith('user.'))

    def fetch_accounts(self,
                       target = None,
                       action = None,
                       type = None,
                       filters = None,
                       references = None,
                       since = None,
                       till = None):
        return self._fetch(target=target,
                           action=action,
                           type=type,
                           filters=filters,
                           references=references,
                           since=since,
                           till=till,
                           guid_filter=lambda guid: guid.startswith('account.'))

    def _get_event_types(self,
                         target,
                         action,
                         type,
                         filters):
        if target is not None or action is not None or type is not None:
            if filters is not None:
                raise KeyError('filters or target/action/type should be set, not both')
            elif ((target is not None and target not in EventTarget) or
                  (action is not None and action not in EventAction) or
                  (type is not None and type not in EventType)):
                raise ValueError('target/action/type should be None or from op.events.target/action.type respectively, got: {0}, {1}, {2}'.format(target,
                                                                                                                                                  action,
                                                                                                                                                  type))
            else:
                event_types = '({target},{action},{type})'.format(target=target if target is not None else '',
                                                                  action=action if action is not None else '',
                                                                  type=type if type is not None else '')
        else:
            if filters is None:
                event_types = '(,,)' #All events
            else:
                if not isinstance(filters, list):
                    raise ValueError('filters should be list of tuples of (op.events.target, op.events.action, op.event.type), got: {0}'.format(filters))
                event_types = []
                for target, action, type in filters:
                    if ((target is not None and target not in EventTarget) or
                        (action is not None and action not in EventAction) or
                        (type is not None and type not in EventType)):
                        raise ValueError('filters should be list of tuples of (op.events.target|None, op.events.action|None, op.event.type|None), got: {0}'.format(filters))
                    else:
                        event_types.append('({target},{action},{type})'.format(target=target if target is not None else '',
                                                                               action=action if action is not None else '',
                                                                               type=type if type is not None else ''))
                event_types = ';'.join(event_types)
        return event_types

    def _fetch(self,
               target = None,
               action = None,
               type = None,
               filters = None,
               references = None,
               since = None,
               till = None,
               guid_filter = lambda guid : True):
        event_types = self._get_event_types(target,
                                            action,
                                            type,
                                            filters)
        if references is None:
            pass
        elif isinstance(references, (list, tuple)):
            references = ','.join(references)
        else:
            raise TypeError('references: expected list or tuple, got: {0}'.format(type(references)))
                
        if isinstance(since, (datetime.datetime, datetime.date)):
            from_timestamp = int(time.mktime(since.timetuple()))
        elif since is None:
            from_timestamp = None
        else :
            raise TypeError('since should be datetime.datetime or datetime.date, got {0}'.format(since))

        if isinstance(till, (datetime.datetime, datetime.date)):
            to_timestamp = int(time.mktime(till.timetuple()))
        elif till is None:
            to_timestamp = None
        else :
            raise TypeError('till should be datetime.datetime or datetime.date, got {0}'.format(till))

        return DatabaseObjects(self._ctx,
                               event_types=event_types,
                               references=references,
                               from_timestamp=from_timestamp,
                               to_timestamp=to_timestamp,
                               guid_filter=guid_filter)

        
        

class DatabaseObjects(object):
    def __init__(self,
                 ctx,
                 event_types,
                 references,
                 from_timestamp,
                 to_timestamp,
                 guid_filter):
        self._ctx = ctx

        self._first_response = self._ctx.gjp.fetch_events(method='list_objects',
                                                          event_types=event_types,
                                                          references=references,
                                                          from_timestamp=from_timestamp,
                                                          to_timestamp=to_timestamp)
        self._guid_filter = guid_filter

    @property
    def empty(self):
        if 'resumption_token' in self._first_response:
            return False
        else :
            return len([guid for guid in self._first_response['items'] if self._guid_filter(guid)]) == 0

    def __bool__(self):
        return not self.empty
    
    @property
    def execution_timestamp(self):
        return datetime.datetime.fromtimestamp(self._first_response['execution_timestamp'])
    
    def __iter__(self):
        return ObjectsIterator(self._ctx,
                               self._first_response,
                               self._guid_filter)

class ObjectsIterator(object):
    def __init__(self,
                 ctx,
                 first_response,
                 guid_filter):
        self._ctx = ctx
        self._items = first_response['items']
        self._items.reverse()
        self._resumption_token = first_response.get('resumption_token', None)
        self._guid_filter = guid_filter

        self._old_news = set()

    def _next_guid(self):
        if self._items:
            return self._items.pop()
        else:
            if self._resumption_token is not None:
                response = self._ctx.gjp.fetch_events('list_objects',
                                                      resumption_token=self._resumption_token)
                self._items = response['items']
                self._items.reverse()
                self._resumption_token = response.get('resumption_token', None)
                if self._items:
                    return self._items.pop()
                else:
                    raise StopIteration()
            else:
                raise StopIteration()
                
    def __next__(self):
        guid = self._next_guid()
        while ((guid in self._old_news) or not self._guid_filter(guid)):
            guid = self._next_guid()
        self._old_news.add(guid)
        if guid.startswith('document.'):
            return self._ctx.documents.load(guid, fetch=False)
        elif guid.startswith('user.'):
            return self._ctx.users.load(guid, fetch=False)
        elif guid.startswith('account.'):
            return self._ctx.accounts.load(guid, fetch=False)
        else:
            raise RuntimeError('Unexpected GUID: {0}'.format(guid))
        
    
class EventsList(list):
    class Event(object):
        def __init__(self,
                     target,
                     action,
                     type,
                     timestamp,
                     guid):
            self._target = target
            self._action = action
            self._type = type
            self._timestamp = timestamp
            self._guid = guid
            
        @property
        def target(self):
            return self._target
    
        @property
        def action(self):
            return self._action
    
        @property
        def type(self):
            return self._type
    
        @property
        def timestamp(self):
            return self._timestamp
    
        @property
        def guid(self):
            return self._guid

    def __init__(self,
                 execution_timestamp):
        super(EventsList, self).__init__([])
        self._execution_timestamp = execution_timestamp

    @property
    def execution_timestamp(self):
        return self._execution_timestamp


