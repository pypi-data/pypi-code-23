from .core.enums import EventTarget, EventAction, EventType, EventResult

class ObjectEvents(object):
    def __init__(self,
                 database_object):
        self._database_object = database_object

    def last_event(self,
                   target = None,
                   action = None,
                   type = None,
                   filters = None):
        return self._database_object.context.events.last_event(target=target,
                                                               action=action,
                                                               type=type,
                                                               filters=filters,
                                                               references=[self._database_object.guid])

    def fetch(self,
              target = None,
              action = None,
              type = None,
              filters = None,
              since = None,
              till = None):
        return self._database_object.context.events.fetch(target=target,
                                                          action=action,
                                                          type=type,
                                                          filters=filters,
                                                          references=[self._database_object.guid],
                                                          since=since,
                                                          till=till)
              

    def trigger(self,
                target,
                action,
                type,
                note = None):
        if target is not None and target not in EventTarget:
            raise ValueError('target should be on of op.events.target, got: {0}'.format(target))

        if action is not None and action not in EventAction:
            raise ValueError('action should be on of op.events.action, got: {0}'.format(action))
        if type is not None and type not in EventType:
            raise ValueError('type should be on of op.events.type, got: {0}'.format(type))
        if note is not None and not isinstance(note, str):
            raise TypeError('note should be instance of str/unicode or None, got: {0}'.format(note))
        self._database_object.context.gjp.trigger_event(self._database_object.guid,
                                                        target=target,
                                                        action=action,
                                                        type=type,
                                                        note=note)
                                                 
    def log(self,
            target,
            action,
            type,
            result,
            note = None):
        if target is not None and target not in EventTarget:
            raise ValueError('target should be on of op.events.target, got: {0}'.format(target))
        if action is not None and action not in EventAction:
            raise ValueError('action should be on of op.events.action, got: {0}'.format(action))
        if type is not None and type not in EventType:
            raise ValueError('type should be on of op.events.type, got: {0}'.format(type))
        if result is not None and result not in EventResult:
            raise ValueError('result should be on of op.events.result, got: {0}'.format(result))
        if note is not None and not isinstance(note, str):
            raise TypeError('note should be instance of str/unicode or None, got: {0}'.format(note))
        self._database_object.context.gjp.log_event(self._database_object.guid,
                                                    target=target,
                                                    action=action,
                                                    type=type,
                                                    result=result,
                                                    note=note)
                                                 
            
