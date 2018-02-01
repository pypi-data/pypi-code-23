"""webHook module.

This module contains the entities which organize web resource to receive
updates from Telegram API, and helpers function to control webHook parameters.
To create the Site object, use the web_hook function.

"""


import json

import requests
from twisted.internet import reactor, task
from twisted.web.resource import Resource, ErrorPage
from twisted.web.server import NOT_DONE_YET, Site

from .url import get_url
from .api import MessageHandler
from .content import (
    Message, InlineQuery, CallbackQuery, ChosenInlineResult, ShippingQuery,
    PreCheckoutQuery
)


def web_hook(path, handler=None):
    """Creates site for webhook mode.

    :param path: webhook path.
    :param handler: Function. If uses, then MessageHandler decorator
        will not be works. It's need if you want handling all messages in one
        function.
    :return: Site.

    """
    root = _RootResource()
    bot_resource = _BotResource(handler)
    root.putChild(path, bot_resource)
    return Site(root)


# def _get_url(token, method):
#     return get_url().format(token=token, method=method)
    # return _url.format(token=token, method=method)


def set_webhook(token, web_hook_url, certificate=None, max_connections=None,
                allowed_updates=None, ):
    """Use this method to specify a url and receive incoming updates via an
    outgoing webHook.

    :param token: Bot token,
    :param web_hook_url: HTTPS url to send updates to. Use an empty string to
        remove webHook integration.
    :param certificate: Upload your public key certificate so that the root
        certificate in use can be checked.
    :param max_connections: Maximum allowed number of simultaneous HTTPS
        connections to the webHook for update delivery, 1-100. Defaults to 40.
    :param allowed_updates: List the types of updates you want your bot to
        receive. For example, specify ['message', 'edited_channel_post',
        'callback_query'] to only receive updates of these types.
    :return: dict.

    """
    url = get_url(token=token, method='setWebHook')
    keys = ('url', 'max_connection', 'allowed_updates')
    values = (web_hook_url, max_connections, allowed_updates)
    data = {key: value for key, value in zip(keys, values) if value}
    cert = {'certificate': open(certificate, 'rb')} if certificate else None
    return requests.post(url=url, data=data, files=cert).json()


def delete_webhook(token):
    """Use this method to remove webHook integration if you decide to switch
    back to get_updates.

    :param token: Bor token.
    :return: dict.

    """
    return requests.post(
        url=get_url(token=token, method='deleteWebHook')).json()


def get_webhook_info(token):
    """Use this method to get current webHook status.

    :param token: Bot token.
    :return: dict.

    """
    return requests.get(
        url=get_url(token=token, method='getWebHookInfo')).json()


class _ErrorResponse(ErrorPage):
    """This class is used to represent errors of incoming requests."""

    def render(self, request):
            request.setResponseCode(self.code)
            request.setHeader('Content-Type', 'application/json')
            body = json.dumps(
                {'code': self.code, 'brief': self.brief, 'detail': self.detail}
            )
            return body.encode()


class _RootResource(Resource):
    """Root resource."""

    def getChild(self, path, request):
        path = path.decode()
        if request.method == b'POST':
            if path in self.children:
                resource = self.children[path]
            else:
                resource = _ErrorResponse(404, 'Not Found',
                                          'Resource not found.')
        else:
            resource = _ErrorResponse(
                405, 'Method Not Allowed',
                'Method %s not allowed.' % request.method.decode()
            )
        return resource


class _BotResource(Resource):
    """Bot resource. Handles incoming requests to the bot."""

    isLeaf = True

    _MESSAGE_TYPES = {
        'message': Message,
        'edited_message': Message,
        'inline_query': InlineQuery,
        'callback_query': CallbackQuery,
        'chosen_inline_result': ChosenInlineResult,
        'shipping_query': ShippingQuery,
        'pre_checkout_query': PreCheckoutQuery
    }

    def __init__(self, handler=None):
        """Initial instance.

        :param handler: Function.

        """
        super(_BotResource, self).__init__()
        self._handler = handler or MessageHandler.handler

    def render_POST(self, request):
        """Receives requests.

        :param request: Request instance.
        :return: Requests are processed asynchronously so this method should
            return NOT_DONE_YET.

        """
        deferred = task.deferLater(reactor, 0.1, self._request_handler,
                                   request)
        deferred.addCallbacks(self._handler, self._error_handler,
                              errbackArgs=(request,))
        return NOT_DONE_YET

    @staticmethod
    def _request_handler(request):
        """Handling request.

        :param request: Request instance.
        :return: one instance from _MESSAGE_TYPES.

        """
        body = request.content.read()
        if not hasattr(json, 'JSONDecodeError'):
            # For Python versions lower than 3.5.
            json.JSONDecodeError = ValueError
        try:
            body_dict = json.loads(body.decode())
        except (TypeError, json.JSONDecodeError):
            raise ValueError
        else:
            if isinstance(body_dict, dict):
                msg_type, msg_dict = [
                    (_BotResource._MESSAGE_TYPES[m_type], body_dict[m_type])
                    for m_type in _BotResource._MESSAGE_TYPES
                    if m_type in body_dict][0]
                try:
                    message = msg_type(**msg_dict)
                except (KeyError, TypeError):
                    raise ValueError
            else:
                raise ValueError
        request.finish()
        return message

    @staticmethod
    def _error_handler(failure, request):
        """Handling error.

        :param failure: Failure instance.
        :param request: Request instance.

        """
        failure.trap(ValueError)
        resp_body = _ErrorResponse(
            400, 'Bad Request', 'Incorrect body value').render(request)
        request.write(resp_body)
        request.finish()
