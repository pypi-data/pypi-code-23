import sys
import json
import traceback
from bson import json_util


class BujectError(Exception):
    def __init__(self, error, detail=None, **kwargs):
        action = kwargs.get('action', '')
        self.detail = detail
        if action:
            self.action_name = action.name
            self.action_param = action.param
        else:
            self.action_name = kwargs.get('action_name', '')
            self.action_param = kwargs.get('action_param', '')

        # self.action.error = {
        #     'message': error,
        #     'detail': detail
        # }
        # self.action.set_end()

        # передаем стек из другой ошибки
        self.stack = []
        first_error = kwargs.get('error', None)
        if first_error and isinstance(first_error, BujectError):  # сохраняем первичную ошибку
            self.stack = first_error.stack
            # if len(self.stack):
            #     self.stack[0]['msg'] = error.msg
            #     self.stack[0]['code'] = error.code
            #     self.stack[0]['category'] = error.category
        # else:

        if isinstance(error, BujectError):
            # прокидываем ошибку наверх
            self.stack += error.stack
            self.msg = error.msg
            # self.param = kwargs.get('param', None)
            self.category = error.category
            self.code = error.code
            self.detail = error.detail
        elif isinstance(error, str):
            self.msg = error
        elif isinstance(error, Exception):
            self.msg = str(error)
            # self.detail = info[len(info)-2]
            # if not self.action_name:
            #     exc_info = sys.exc_info()
            #     info = traceback.format_exception(*exc_info)
            #     self.action_name = info[len(info)-2]
            # if not self.action_param:
            # self.action_param = str(exc_info[2].tb_frame.f_locals)
        elif isinstance(error, bytes):
            self.msg = error.decode()
        else:
            self.msg = "Класс ошибок получил непредвиденное исключение"
        exc_info = sys.exc_info()
        info = traceback.format_exception(*exc_info)
        self.action_info = info[len(info) - 2]

        # if self.action_name:
        self.stack.append({
            'action_name': self.action_name,
            'action_info': self.action_info,
            'detail': detail,
            'action_param': self.action_param,
        })
        if not hasattr(self, 'code'):
            self.category = 'BUJECT_ERROR'
            self.code = 603
            self.detail = detail

    def __str__(self):
        res = '{0}:{1} {2}'.format(self.code, self.category, self.msg)
        if self.detail:
            res += ' ' + self.detail
        # res += '\n'
        # res += 'Stack:\n'
        # for elem in self.stack:
        #     res += '   {0} {1}\n'.format(elem.get('action_name', ''), elem.get('detail', ''))
        #     res += '      {0}\n'.format(elem.get('action_info', ''))
        return res
        # return repr('{0}:{1} {2} {3}'.format(self.code, self.category, self.msg, self.detail if self.detail else ''))

    def dump(self):
        return json_util.dumps(self.to_json(), ensure_ascii=False)

    def to_json(self):
        return {
            'error': {
                'message': self.msg,
                'detail': str(self.detail),
                'stack': self.stack,
                'code': self.code,
                'category': self.category
            }
        }

    @staticmethod
    def get_code(category):
        try:
            code = {
                'USER_ERROR': 601,
                'BUBOT_ERROR': 602,
                'BUJECT_ERROR': 603,
                'EXTERNAL_ERROR': 604,
                'TEMPORARY_ERROR': 501,
                'SETTINGS_ERROR': 502,
            }
            return code[category.upper()]
        except Exception:
            raise BubotError("Запрос кода несуществующего исключения")


class UserError(BujectError):
    def __init__(self, msg, detail=None, **kwargs):
        super().__init__(msg, detail, **kwargs)
        self.category = 'USER_ERROR'
        self.code = 601


class BubotError(BujectError):
    def __init__(self, msg, detail=None, **kwargs):
        super().__init__(msg, detail, **kwargs)
        self.category = 'BUBOT_ERROR'
        self.code = 602


class SettingsError(BujectError):
    def __init__(self, msg, detail=None, **kwargs):
        super().__init__(msg, detail, **kwargs)
        self.category = 'SETTINGS_ERROR'
        self.code = 502


class ExternalError(BujectError):
    def __init__(self, msg, detail=None, **kwargs):
        super().__init__(msg, detail, **kwargs)
        self.category = 'EXTERNAL_ERROR'
        self.code = 604


class TemporaryError(BujectError):
    def __init__(self, msg, detail=None, **kwargs):
        super().__init__(msg, detail, **kwargs)
        self.category = 'TEMPORARY_ERROR'
        self.code = 501
