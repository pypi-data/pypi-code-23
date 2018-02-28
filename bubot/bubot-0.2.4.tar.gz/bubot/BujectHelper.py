import os
import json
import copy
from bubot.BujectError import BujectError, UserError, BubotError, BujectError
from bubot.Action import Action
from datetime import datetime, timedelta
import asyncio
import inspect


def load_config(config_type, cache, name=None, user_config=None):
    if name:
        base_config, cache = read_cache_config("./{0}/{1}/{1}.json".format(config_type, name), cache)
        if user_config:
            user_config, cache = update_config(config_type, name, base_config, user_config, cache)
            return user_config, cache
    else:
        base_config, cache = read_cache_config(get_path_default_config(config_type), cache)
        name = config_type
        base_config, cache = update_config(config_type, name, {}, base_config, cache)
    return base_config, cache


def read_config(path):
    try:
        with open(path, encoding='utf-8') as config_file:
            result = config_file.read()
            result = json.loads(result)
            return result
    except Exception as e:
        raise UserError(str(e), 'BubotConfig.read_config({0}): {1}'.format(path, str(e)))


def read_cache_config(path, cache):
    try:
        config = cache[path]
    except KeyError:
        cache[path] = read_config(path)
        config = cache[path]

    return copy.deepcopy(config), cache


def get_path_default_config(_config_type):
    return '{0}{1}.json'.format(os.path.realpath(__file__)[:-15], _config_type)

# def get_base_config(config_type, config_name, base_config, new_config, cache):
#     try:
#         parent_name = None
#         parent_config = None
#         base_config, cache = read_cache_config("./{0}/{1}/{1}.json".format(config_type, config_name), cache)
#
#
#
#     except BujectError as e:
#         raise BujectError(e, 'update_config({0}, {1})'.format(config_type, config_name))
#     except Exception as e:
#         raise UserError(str(e), 'update_config({0}, {1})'.format(config_type, config_name))


# рекурсивно переопределяем параметры конфига, значаниями из data
def update_config(config_type, config_name, base_config, new_config, cache):
    try:
        parent_name = None
        parent_config = None

        if new_config:
            if 'param' in new_config \
                    and 'parent' in new_config['param'] \
                    and new_config['param']['parent']['value']:  # если в новом конфиге указан родитель
                parent_name = new_config['param']['parent']['value']
                if parent_name.lower() == config_type:
                    parent_name = config_type
                    parent_config, cache = read_cache_config(get_path_default_config(config_type), cache)
                else:
                    parent_config, cache = read_cache_config("./{0}/{1}/{1}.json".format(config_type, parent_name), cache)
        if not parent_name:  # если родитель не указан (это родитель)
            if config_type != config_name:  # если это ещё не конфиг типа, то берем конфиг типа
                parent_name = config_type
                parent_config, cache = read_cache_config(get_path_default_config(config_type), cache)
            # else: # если это ещё не конфиг buject, берем его
            #     if config_name != 'buject':
            #         parent_name = 'buject'
            #         config_type = 'buject'
            #         parent_config, cache = read_cache_config(get_path_default_config(config_type), cache)

        if config_type != config_name and parent_name:
            base_config, cache = update_config(config_type, parent_name, parent_config, base_config, cache)

        if not base_config:
            return copy.deepcopy(new_config), cache

        if new_config:
            for folder in new_config:
                if isinstance(new_config[folder], dict):
                    if folder not in base_config:
                        base_config[folder] = {}
                    # if os.path.exists('./{0}'.format(folder)):  # если данной папки есть свои конфиги, берем их
                    #     if folder not in base_config:
                    #         base_config[folder] = {}
                    #     for element in new_config[folder]:
                    #         if element not in base_config[folder]:
                    #             base_config[folder][element] = {}
                    #         base_config[folder][element], cache = update_config(folder, element,
                    #                                                             base_config[folder][element],
                    #                                                             new_config[folder][element], cache)
                    else:
                        base_config[folder] = update_dict(base_config[folder], new_config[folder])

                elif isinstance(new_config[folder], list):
                    base_config[folder] = copy.deepcopy(new_config[folder])
                else:
                    base_config[folder] = new_config[folder]
        return base_config, cache

    except BujectError as e:
        raise BujectError(e, 'update_config({0}, {1})'.format(config_type, config_name))
    except Exception as e:
        raise UserError(str(e), 'update_config({0}, {1})'.format(config_type, config_name))


def update_dict(base, new):
    if not new:
        return base
    for element in new:
        try:
            if element in base:
                if isinstance(new[element], dict):
                    try:
                        base[element] = update_dict(base[element], new[element])
                    except BujectError as e:
                        raise BujectError(e, 'BubotConfig.update_dict({0})'.format(element))
                    except Exception as e:
                        raise UserError(str(e), 'BubotConfig.update_dict({0})'.format(element))
                # elif isinstance(new[element], list):
                #     pass
                else:
                    base[element] = new[element]
            else:
                try:
                    base[element] = copy.deepcopy(new[element])
                except TypeError as e:
                    if not base:
                        base = {
                            element: copy.deepcopy(new[element])
                        }
                    else:
                        raise BujectError(e, 'copy.deepcopy({0})'.format(element))
                except BujectError as e:
                    raise BujectError(e, 'copy.deepcopy({0})'.format(element))
                except Exception as e:
                    raise UserError(str(e), 'copy.deepcopy({0})'.format(element))
        except BujectError as e:
            raise BujectError(e, action_name='BubotConfig.update_dict', action_param=element)
        except Exception as e:
            raise UserError('Bad dict', 'element "{0}": {1}'.format(element, str(e)),
                            action_name='BubotConfig.update_dict')
    return base


def copy_dict(config):
    return copy.deepcopy(config)


def config_to_simple_dict(config):
    result = {}
    for element in config:
        if isinstance(config[element], dict):
            if "value" in config[element]:
                result[element] = config[element]["value"]
            else:
                result[element] = config_to_simple_dict(config[element])
        else:
            result[element] = config[element]
    return result


def get_buject(buject_name, buject_type="buject"):
    return get_class('{0}.{1}.{1}.{1}'.format(buject_type, buject_name))


def get_class(kls):
    try:
        parts = kls.split('.')
        module = ".".join(parts[:-1])
        m = __import__(module)
        for comp in parts[1:]:
            m = getattr(m, comp)
        return m
    except ImportError as e:
        # ошибки в классе  или нет файла
        raise ImportError('get_class({0}: {1})'.format(kls, str(e)))
    except AttributeError as e:
        # Нет такого класса
        raise AttributeError('get_class({0}: {1})'.format(kls, str(e)))
    except Exception as e:
        # ошибки в классе
        raise BujectError(str(e), 'get_class({0}: {1})'.format(kls, str(e)))


# async def get_redis(host, port, db):
#     try:
#         return await asyncio.wait_for(asyncio_redis.Connection.create(host=host, port=port, db=db), 1)
#     except asyncio.futures.TimeoutError:
#         raise TimeoutError('Redis.Connection({0}:{1}))'.format(host, port, db))
#
#
#
# def get_bubot_config(name, user_config=None):
#     path = "./config/" if os.curdir == "." else ""
#     return get_config(path, name, user_config)
#
#
# def get_default_bubot_config():
#     path = "./engine/" if os.curdir == "." else ""
#     return get_config(path, "default_config")
#
#
# def get_buject_config(name, user_config=None):
#     path = "./buject/" if os.curdir == "." else ""
#     return get_config(path, name, user_config)


def get_available_worker():
    return get_available_config("worker")#, "./buject/" if os.curdir == "." else "")


def get_available_buject():
    return get_available_config("buject")#, "./buject/" if os.curdir == "." else "")


def get_available_ui():
    return get_available_config("ui")


# def get_available_bubot():
#     return get_available_config("./config/")


def get_available_config(config_type):
    config = {}
    path = "./{0}/".format(config_type)
    _files = os.listdir(path)
    for name in _files:
        config_path = "{0}{1}/{1}.json".format(path, name)
        if os.path.isdir("{0}{1}".format(path, name)) and os.path.exists(config_path):
            try:
                buject_config = read_config(config_path)
                if name not in config:
                    config[name], cache = update_config(config_type, name, {}, buject_config, {})
            except Exception as e:
                config[name] = {'error': str(e)}
    return config


def create_user_config(new_bubot_config, available_buject):
    res = {}
    for _group in ['param', 'outgoing_event', 'incoming_event', 'incoming_request', 'outgoing_request']:
        if _group in new_bubot_config:
            _res = compare_dict(available_buject['Bubot'][_group], new_bubot_config[_group])
            if _res:
                res[_group] = copy.deepcopy(_res)

    if 'depend_buject' in new_bubot_config:
        res['depend_buject'] = {}
        for _buject in new_bubot_config['depend_buject']:
            _depend_buject = new_bubot_config['depend_buject'][_buject]
            if 'bubot' in _depend_buject:
                _depend_buject.pop('bubot')  # убираем параметры бубота из каждого объекта
            _base_buject = _depend_buject['param']['buject']['value']
            res['depend_buject'][_buject] = compare_dict(available_buject[_base_buject], _depend_buject)
            if 'param' not in res['depend_buject'][_buject]:
                res['depend_buject'][_buject]['param'] = {}
            res['depend_buject'][_buject]['param']['buject'] = {'value': _base_buject}
            # res['depend_buject'][_buject]['param']['name'] = {'value': _depend_buject['param']['name']['value']}

    return res


def compare_dict(base, new):
    res = {}
    for elem in new:
        try:
            if base and elem in base:
                if isinstance(new[elem], dict):
                    _res = compare_dict(base[elem], new[elem])
                    if _res:
                        res[elem] = copy.deepcopy(_res)
                else:
                    if new[elem] != base[elem]:
                        res[elem] = new[elem]
            else:
                res[elem] = new[elem]
        except Exception as e:
            raise BujectError('compare_dict: {0}'.format(str(e)), elem)
    return res


def convert_ticks_to_datetime(ticks):
    return datetime(1, 1, 1) + timedelta(microseconds=ticks // 10)


def async_test(f):
    def wrapper(*args, **kwargs):
        loop = asyncio.get_event_loop()
        kwargs['loop'] = loop
        if inspect.iscoroutinefunction(f):
            future = f(*args, **kwargs)
        else:
            coroutine = asyncio.coroutine(f)
            future = coroutine(*args, **kwargs)
        loop.run_until_complete(future)

    return wrapper


async def run_buject(buject_id, config, owner, run_in_loop=True):
    res = Action('BujectHelper.run_buject')
    # try:
    buject_class = get_buject(config['param']['buject'])
    buject_class = buject_class(id=buject_id, config=config, bubot=owner.bubot, loop=owner.loop)
    buject_class.init()
    res.result = {
        'class': buject_class,
        'task': None
    }
    if run_in_loop:
        res.result['task'] = owner.loop.create_task(buject_class.handler())
    else:
        res.result['task'] = buject_class.handler()
    return res.set_end()
    # except Exception as e:
    #     await self.error("worker.run_buject({0}):{1}".format(buject_id, str(e)))


async def run_action(buject_id, config, action, action_data, owner, run_in_loop=True):
    res = Action('BujectHelper.run_buject')

    buject_class = get_buject(config['param']['buject'])
    buject_class = buject_class(id=buject_id, config=config, bubot=owner.bubot, loop=owner.loop)
    buject_class.init()
    res.result = {
        'class': buject_class,
        'task': None
    }
    _action = getattr(buject_class, 'action_{0}'.format(action))
    if run_in_loop:
        res.result['task'] = owner.loop.create_task(_action(action_data))
    else:
        res.result['task'] = _action(action_data)
    return res.set_end()


if __name__ == '__main__':
    # config = load_config("bubot", "test")
    # config = config_to_simple_dict(config)

    # a = get_available_ui()
    f = 1

    # a = {"param": {"name": {"value": "XXX"}}}
    # b = {"param": {"name": {"value": "XXX"}}}
    # c = compare_dict(a, b)
    # test = True
