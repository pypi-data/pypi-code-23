#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2018-02-07
# @Author  : yaolu (yaolu0405@gmail.com)


import inspect
import types
import ast
import traceback
import smtplib
from email.mime.text import MIMEText


class _ReWriteNode(ast.NodeTransformer):
    def __init__(self, *args, **kwargs):
        self.func_name = kwargs.get('func_name')
        self.lineno = kwargs.get('lineno') or 0

    def generic_visit(self, node):
        ast.NodeTransformer.generic_visit(self, node)
        return node

    def visit_FunctionDef(self, node):
        if node.name == self.func_name or self.func_name == None:
            ast.increment_lineno(node, self.lineno)
            newnode = ast.FunctionDef(name=node.name, args=node.args, decorator_list=node.decorator_list, returns=node.returns)
            _body = node.body

            _func = ast.Attribute(value=ast.Name(id="MailAlert", ctx=ast.Load()), attr='send', ctx=ast.Load())
            _arg_func = ast.Attribute(value=ast.Name(id="traceback", ctx=ast.Load()), attr='format_exc', ctx=ast.Load())
            _arg_call = ast.Call(func=_arg_func, args=[], keywords=[])
            call = ast.Call(func=_func, args=[_arg_call], keywords=[])
            _expr = ast.Expr(value=call)
            _raise = ast.Raise(exc=None, cause=None)
            except_ast_node = ast.ExceptHandler(name="", type=None, body=[_expr, _raise])
            newbody = []
            try_node = ast.Try(body=_body, orelse=[], finalbody=[], handlers=[except_ast_node])

            newbody.append(try_node)
            newnode.body = newbody
            # ast.copy_location(newnode, node)
            ast.fix_missing_locations(newnode)
            return newnode
        else:
            return node


class _MyMetaClass(type):
    def _send(self, obj):
        # print('self = ', self)
        if isinstance(obj, type):
            # if obj is a class
            # print(inspect.currentframe().f_back.f_code.co_firstlineno)
            info = inspect.getframeinfo(inspect.stack()[1][0])
            # file_path = os.path.abspath(sys.modules[obj.__module__].__file__)

            ast_code = ast.parse(inspect.getsource(obj))
            visitor = _ReWriteNode(lineno=info.lineno)
            root = visitor.visit(ast_code)
            code_obj = compile(root, info.filename, "exec")
            exec(code_obj)

            return locals()[obj.__name__]
        elif isinstance(obj, object):
            def __func(*args, **kwargs):
                try:
                    return obj(*args, **kwargs)
                except Exception as e:
                    self.send(traceback.format_exc())
                    raise

            return __func

    def __call__(self, *args, **kwargs):
        self._mail_group = kwargs.get('to')
        self._cc_group = kwargs.get('cc')

        return self._send


class MailAlert(metaclass=_MyMetaClass):
    @classmethod
    def send(cls, error_msg):
        try:
            import mail_settings as ms
        except:
            print("can not find fild mail_setting.py in python sys.path, please create mail_settings.py then add its path to sys.path")
            return
        _mail_group = cls._mail_group
        _cc_group = cls._cc_group
        # get mail list
        msg = MIMEText(error_msg)
        msg['Subject'] = 'project error'
        msg['From'] = ms.server['user']
        msg['To'] = ','.join(getattr(ms, _mail_group))

        if _cc_group:
            if isinstance(_cc_group, str):
                msg['Cc'] = ','.join(getattr(ms, _cc_group))
            elif isinstance(_cc_group, list):
                _tmp = []
                for _cc in _cc_group:
                    _tmp.extend(getattr(ms, _cc))
                msg['Cc'] = ','.join(_tmp)
        else:
            msg['Cc'] = ''

        if ms.server['ssl']:
            smtp = smtplib.SMTP_SSL()
        else:
            smtp = smtplib.SMTP()

        smtp.connect(ms.server['name'], ms.server['port'])
        smtp.login(ms.server['user'], ms.server['password'])
        smtp.sendmail(msg['From'], msg['To'].split(',') + msg['Cc'].split(','), msg.as_string())
        smtp.close()
