import asyncio
import json
import os

import aiohttp
import aiohttp_jinja2
from aiohttp import web
from aiohttp.web import json_response, Response, WebSocketResponse, View, HTTPFound, HTTPUnauthorized
from aiohttp_session import get_session

from bubot.Buject import Buject
from bubot.BujectError import BujectError
from urllib.parse import unquote


class Ui(View, Buject):
    def __init__(self, request):
        View.__init__(self, request)
        Buject.__init__(self)
        self.param['log'] = 0
        self.type = 'ui'
        self.config = {}
        self.bubot = self.request.app['bubot']
        self.broker = self.request.app['bubot'].broker
        self.db = self.request.app['bubot'].db
        self.session = None
        self.user = None
        self.ws = None
        pass

    @staticmethod
    def add_route(app, ui_name, ui_view):
        # if os.path.isfile('./ui/{0}/{0}.py'.format(ui_name)):
        #     ui_view = BubotConfig.get_class('ui.{0}.{0}.{0}'.format(ui_name))
        # else:
        #     ui_view = Ui
        ui_base_url = '/ui/{0}'.format(ui_name)
        static_path = '{0}/static/'.format(ui_base_url)
        if os.path.exists("." + static_path):
            app.router.add_static(static_path, "." + static_path)
        app.router.add_route('*', ui_base_url, ui_view)
        app.router.add_route('*', '/{ws}' + ui_base_url + '/{method}', ui_view)
        app.router.add_route('*', ui_base_url + '/{method}', ui_view)

    @staticmethod
    def need_auth(request):
        return False

    async def get_render_context(self):
        return {}

    async def get(self):
        # ui = BubotConfig.get_available_ui()
        template = self.request.match_info.get('method', "index")
        if self.request.match_info.get('ws', False):
            return await self.web_socket(self.request)
        if template[-4:] == 'html':
            try:
                render_context = await self.get_render_context()
                response = aiohttp_jinja2.render_template(
                    '{0}/{1}.jinja2'.format(self.__class__.__name__, template[:-5]),
                    self.request, render_context)
                response.headers['Content-Language'] = 'ru'

                return response
            except Exception as e:
                return Response(text=str(e), status=400)

        # self.bubot = self.request.app['bubot'].bubot
        # self.redis = self.request.app['bubot'].redis
        # self.db = self.request.app['bubot'].db
        method = 'ui_{0}'.format(template)
        try:
            return await getattr(self, method)(self.request.GET)
        except Exception as e:
            msg = 'Error in ui.{0}.post({1}): {2}'.format(self.__class__.__name__, method, e)
            return web.Response(text=msg, status=400)

    async def post(self):
        method = self.request.match_info.get('method')
        try:
            method = 'ui_{0}'.format(method)
            if self.request.content_type == 'application/json':
                data = await self.request.json()
            else:
                data = await self.request.text()
            return await getattr(self, method)(data)
        except asyncio.TimeoutError:
            msg = 'Timeout in ui.{0}.post({1})'.format(self.__class__.__name__, method)
            return web.Response(text=msg, status=408)
        except BujectError as e:
            return web.Response(text=e.dump(), status=400)
        except Exception as e:
            error = BujectError('Error in ui.{0}.post({1}): {2}'.format(self.__class__.__name__, method, e))
            return web.Response(text=error.dump(), status=400)

    async def web_socket(self, request):
        if self.__class__.__name__ in self.request.app['ui']:
            self.config = self.request.app['ui'][self.__class__.__name__]
            self.param = self.config['param']
        self.init()

        self.ws = WebSocketResponse()
        await self.ws.prepare(request)
        print('Connection opened')

        try:
            await asyncio.gather(self.handle_ws(), self.handle_get_redis_msg())
        except Exception as e:  # Don't do except: pass
            a = 1
            # import traceback
            # traceback.print_exc()
        finally:
            print('Connection closed')
        return self.ws

    async def handle_ws(self):
        while True:
            msg = await self.ws.receive()
            if msg.tp != aiohttp.MsgType.text:
                if msg.tp == aiohttp.MsgType.error:
                    print('ws connection closed with exception %s' % self.ws.exception())
                break
            else:
                message = json.loads(msg.data, encoding='utf-8')
                if "method" in message and "param" in message:
                    # if self.get_param('log') > 3:
                    #     await self.log("WebSocket on_message({0})".format(message['method']))
                    if hasattr(self, "ui_{0}".format(message['method'])):
                        try:
                            await getattr(self, "ui_{0}".format(message['method']))(message['param'])
                        except Exception as e:
                            await self.error('socket method ui_{0}: {1}'.format(message['method'], e))
                    else:
                        await self.error('socket method not found ({0})'.format(message['method']))
                        # return True


                        # async def check_redis(self, **kwargs):
                        #     return True

                        # async def handle_get_redis_msg(self):
                        #     await self.check_redis()
                        #     self.subscribe_list = await self.get_subscribe_list()
                        #     if not await self.subscribe():
                        #         return
                        #     while True:
                        #         msg_redis = await self.pubsub.next_published()
                        #         if msg_redis:
                        #             if msg_redis.channel not in self.subscribe_list:
                        #                 self.error('{0}: undeclared channel {1}'.format(self.id, msg_redis.channel))
                        #                 continue
                        #
                        #             self.ws.send_str(msg_redis.value)
                        #     return True


                        # async def subscribe(self):
                        #     if not self.subscribe_list:
                        #         return
                        #     await self.check_redis()
                        #     with (await self.lock_redis):
                        #         if not self.pubsub:
                        #             self.pubsub = await asyncio.wait_for(self.redis.start_subscribe(), 1)
                        #         subscribe_list = []
                        #         for element in self.subscribe_list:
                        #             subscribe_list.append(element)
                        #         await asyncio.wait_for(self.pubsub.subscribe(subscribe_list), 1)

    async def ui_send_request(self, param):
        result = await self.bubot.send_request(**param)
        return json_response(result)

    async def check_right(self, redirect=True):
        self.session = await get_session(self.request)
        session_id = self.session.get("session_id", None)
        if not session_id:
            if redirect:
                url = self.request.app.router['login'].url()
                raise HTTPFound(url)
            else:
                raise HTTPUnauthorized()
        self.user = self.redis.hget('user', session_id)
        if not self.user:
            return False
        return True

    @staticmethod
    def parse_data_param(data):
        data = unquote(data)
        params = {}
        tmp = data.split('&')
        for elem in tmp:
            key, value = elem.split('=', 1)
            params[key] = value
        return params


if __name__ == '__main__':
    # config = load_config("bubot", "test")
    # config = config_to_simple_dict(config)
    pass
    # a = Ui()
