# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import os
from django.db import models
from django.utils import timezone
import logging, requests, json, uuid
from datetime import timedelta, datetime
from . import parsexml, signature

logger = logging.getLogger(__name__)


def attachment_filename(instance, filename):
    file_ext = os.path.splitext(filename)[-1]
    file_name = str(uuid.uuid4()).replace('-', '') + file_ext
    return '%s/%s' % (instance._meta.app_label, file_name)


class Tenant(models.Model):
    chinese_name = models.CharField(max_length=50, help_text=u'中文名称，标示该商户')
    name = models.CharField(max_length=50, unique=True)
    enable = models.BooleanField(default=True)

    # 微信公众号的基础信息
    appid = models.CharField(max_length=200, unique=True)
    secret = models.CharField(max_length=200, unique=True, help_text=u'开发者密码')
    token = models.CharField(max_length=100, help_text=u'令牌', default='')
    encoding_aeskey = models.CharField(blank=True, max_length=200, help_text=u'消息加解密密钥', default='')

    # access_token管理
    _access_token = models.CharField(max_length=200, unique=True, default='', blank=True)
    access_token_expired_at = models.DateTimeField(blank=True, null=True, default=None)

    # jsapi_ticket 管理
    _jsapi_ticket = models.CharField(max_length=200, default='', blank=True)
    jsapi_ticket_expired_at = models.DateTimeField(blank=True, null=True, default=None)

    # 支付相关
    shanghu_id = models.CharField(max_length=50, blank=True, default='', help_text=u'微信支付商户号')
    payment_api_key = models.CharField(max_length=200, blank=True, default='', help_text=u'微信支付商户的API密钥')
    payment_notify_url = models.CharField(max_length=200, blank=True, default='', help_text=u'支付回调接口')
    refund_notify_url = models.CharField(max_length=200, blank=True, default='', help_text=u'退款回调接口')
    apiclient_cert_pem = models.FileField(null=True, blank=True, default=None, upload_to=attachment_filename)
    apiclient_key_pem = models.FileField(null=True, blank=True, default=None, upload_to=attachment_filename)
    apiclient_cert_p12 = models.FileField(null=True, blank=True, default=None, upload_to=attachment_filename)
    rootca_pem = models.FileField(null=True, blank=True, default=None, upload_to=attachment_filename)

    # 微信公众号的菜单按钮
    menu = models.TextField(blank=True, null=True, default=None)

    # 配置管理员
    managers = models.ManyToManyField("Account", blank=True, related_name='parents', help_text=u'设置管理员账号，用于接收通知类消息')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    def __unicode__(self):
        return self.name

    @property
    def access_token(self):
        if self._access_token and self.access_token_expired_at > timezone.now():
            return self._access_token

        url = 'https://api.weixin.qq.com/cgi-bin/token'
        params = {
            'appid': self.appid,
            'secret': self.secret,
            'grant_type': 'client_credential'
        }
        resp = requests.get(url, params=params)
        if resp.status_code != 200:
            logger.error('get access-token failed -- %s %s' % (resp.status_code, resp.content))
            return

        resp_json = resp.json()
        if 'errmsg' in resp_json:
            logger.error('get access-token failed -- %s' % json.dumps(resp_json))
            return

        self._access_token = resp_json['access_token']
        self.access_token_expired_at = timezone.now() + timedelta(seconds=resp_json['expires_in'] - 2)
        self.save()

        return self._access_token

    @property
    def jsapi_ticket(self):
        if self._jsapi_ticket and self.jsapi_ticket_expired_at > timezone.now():
            return self._jsapi_ticket

        if not self.access_token:
            return

        url = 'https://api.weixin.qq.com/cgi-bin/ticket/getticket?type=jsapi'
        params = {
            'access_token': self.access_token
        }
        resp = requests.get(url, params=params)
        if resp.status_code != 200:
            logger.error('get jsapi_ticket failed -- %s %s' % (resp.status_code, resp.content))
            return

        resp_json = resp.json()
        if 'errcode' in resp_json and resp_json['errcode'] != 0:
            logger.error('get jsapi_ticket failed -- %s' % json.dumps(resp_json))
            return

        self._jsapi_ticket = resp_json['ticket']
        self.jsapi_ticket_expired_at = timezone.now() + timedelta(seconds=resp_json['expires_in'] - 2)
        self.save()

        return self._jsapi_ticket


    def get_webauth_openid(self, code):
        url = ' https://api.weixin.qq.com/sns/oauth2/access_token?grant_type=authorization_code'
        params = {
            'code': code,
            'appid': self.appid,
            'secret': self.secret,
        }
        resp = requests.get(url, params=params)
        if resp.status_code != 200:
            logger.error('get openid failed -- %s %s' % (resp.status_code, resp.content))
            return

        resp_json = resp.json()
        if 'errmsg' in resp_json:
            logger.error('get openid failed -- %s' % json.dumps(resp_json))
            return

        return resp_json.get('openid')


    def get_userinfo(self, openid):
        if not self.access_token:
            return

        url = 'https://api.weixin.qq.com/cgi-bin/user/info?lang=zh_CN'
        params = {
            'access_token': self.access_token,
            'openid': openid
        }
        resp = requests.get(url, params=params)
        if resp.status_code != 200:
            logger.error('get userifo failed -- %s %s' % (resp.status_code, resp.content))
            return

        resp_json = resp.json()
        if 'errmsg' in resp_json:
            logger.error('get userifo failed -- %s' % json.dumps(resp_json))
            return

        return resp_json


    def get_openids(self):
        """
        返回一个生成器，每次吐出一个openid
        """
        if not self.access_token:
            return

        url = 'https://api.weixin.qq.com/cgi-bin/user/get'
        params = {
            'access_token': self.access_token,
            'next_openid': ''
        }

        while True:
            logger.debug(u'requests url(%s) params(%s)' % (url, params))
            resp = requests.get(url, params=params)
            if resp.status_code != 200:
                logger.error(u'get openids failed -- %s %s' % (resp.status_code, resp.content))
                return

            resp_json = resp.json()
            if 'errmsg' in resp_json:
                logger.error(u'get openids failed -- %s' % json.dumps(resp_json))
                return

            # 没有关注账号了
            if resp_json.get('count') == 0:
                break

            for i in resp_json['data']['openid']:
                yield i

            # 不需要下一次请求了
            if resp_json.get('count') < 10000:
                break

            params['next_openid'] = resp_json.get('next_openid')


    def get_msg_tpls(self):
        if not self.access_token:
            return

        url = 'https://api.weixin.qq.com/cgi-bin/template/get_all_private_template'
        params = {
            'access_token': self.access_token
        }

        resp = requests.get(url, params=params)
        if resp.status_code != 200:
            logger.error('get MessageTemplates failed -- %s %s' % (resp.status_code, resp.content))
            return

        resp_json = resp.json()
        if 'template_list' not in resp_json:
            logger.error('get MessageTemplates failed -- %s' % json.dumps(resp_json))
            return

        # 设置返回
        return resp_json.get('template_list', [])


    def get_menu(self):
        if not self.access_token:
            return

        url = 'https://api.weixin.qq.com/cgi-bin/menu/get'
        params = {
            'access_token': self.access_token
        }

        resp = requests.get(url, params=params)
        if resp.status_code != 200:
            logger.error('get menu failed -- %s %s' % (resp.status_code, resp.content))
            return

        resp_json = resp.json()
        if not 'menu' in resp_json:
            logger.error('get menu failed -- %s %s' % (resp.status_code, resp.content))
            return

        self.menu = resp.content
        self.save()
        return self


    def delete_menu(self):
        if not self.access_token:
            return

        url = 'https://api.weixin.qq.com/cgi-bin/menu/delete'
        params = {
            'access_token': self.access_token
        }

        resp = requests.get(url, params=params)
        if resp.status_code != 200:
            logger.error('delete menu failed -- %s %s' % (resp.status_code, resp.content))
            return

        resp_json = resp.json()
        if not 'errcode' in resp_json or resp_json.get('errcode') != 0:
            logger.error('delete menu failed -- %s %s' % (resp.status_code, resp.content))
            return

        self.menu = None
        self.save()
        return self


    def create_menu(self):
        if not self.access_token:
            return

        url = 'https://api.weixin.qq.com/cgi-bin/menu/create'
        params = {
            'access_token': self.access_token
        }

        resp = requests.post(url, params=params, data=self.menu.encode('utf-8'))
        if resp.status_code != 200:
            logger.error('create menu failed -- %s %s' % (resp.status_code, resp.content))
            return

        resp_json = resp.json()
        if not 'errcode' in resp_json or resp_json.get('errcode') != 0:
            logger.error('create menu failed -- %s %s' % (resp.status_code, resp.content))
            return
        return self


class Account(models.Model):
    sexes = {
        0: u'未知',
        1: u'男',
        2: u'女'
    }

    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE)
    openid = models.CharField(max_length=100, unique=True)
    nickname = models.CharField(max_length=100)
    sex = models.IntegerField(choices=sexes.items())
    city = models.CharField(max_length=50)
    province = models.CharField(max_length=50)
    country = models.CharField(max_length=50)
    headimgurl = models.CharField(max_length=250)
    subscribed_at = models.DateTimeField()
    unionid = models.CharField(max_length=200)
    remark = models.CharField(max_length=100)
    status = models.CharField(max_length=20, default='subscribe')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return '%s-%s' % (self.tenant.name, self.nickname)

    def __unicode__(self):
        return '%s-%s' % (self.tenant.name, self.nickname)

    @classmethod
    def sync_account(cls, tenant, openid):
        userinfo = tenant.get_userinfo(openid)
        if not userinfo:
            return

        if tenant.account_set.filter(openid=openid):
            user = tenant.account_set.get(openid=openid)
            user.nickname = userinfo['nickname']
            user.sex = userinfo['sex']
            user.city = userinfo['city']
            user.province = userinfo['province']
            user.country = userinfo['country']
            user.headimgurl = userinfo['headimgurl']
            user.unionid = userinfo.get('unionid', '')
            user.remark = userinfo['remark']
            user.status = 'subscribe'
            user.save()
        else:
            user = tenant.account_set.create(
                openid=userinfo['openid'],
                nickname=userinfo['nickname'],
                sex=userinfo['sex'],
                city=userinfo['city'],
                province=userinfo['province'],
                country=userinfo['country'],
                headimgurl=userinfo['headimgurl'],
                subscribed_at=datetime.fromtimestamp(userinfo['subscribe_time'], timezone.get_default_timezone()),
                unionid=userinfo.get('unionid', ''),
                remark=userinfo['remark'],
                status='subscribe'
            )
        return user


class MessageTemplate(models.Model):
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE)
    key = models.CharField(default='', max_length=50)
    template_id = models.CharField(unique=True, max_length=50)
    title = models.CharField(blank=True, default='', max_length=50)
    primary_industry = models.CharField(blank=True, default='', max_length=50)
    deputy_industry = models.CharField(blank=True, default='', max_length=50)
    content = models.TextField(blank=True, default='')
    example = models.TextField(blank=True, default='')
    url = models.CharField(blank=True, default='', max_length=500)

    def __unicode__(self):
        return self.key

    @staticmethod
    def sync_tpl(tenant, item):
        template_id = item['template_id']
        if tenant.messagetemplate_set.filter(template_id=template_id):
            tpl = tenant.messagetemplate_set.get(template_id=template_id)
            tpl.title = item['title']
            tpl.primary_industry = item['primary_industry']
            tpl.deputy_industry = item['deputy_industry']
            tpl.content = item['content']
            tpl.example = item['example']
            tpl.save()
        else:
            tpl = tenant.messagetemplate_set.create(
                template_id=item['template_id'],
                key=item['template_id'],
                title=item['title'],
                primary_industry=item['primary_industry'],
                deputy_industry=item['deputy_industry'],
                content=item['content'],
                example=item['example']
            )
        return tpl


    def send(self, data, account):
        if not self.access_token:
            return

        url = 'https://api.weixin.qq.com/cgi-bin/message/template/send'
        params = {
            'access_token': self.access_token
        }
        req_data = {
            "touser": account.openid,
            "template_id": self.template_id,
            "url": self.url or None,
            "data": data
        }

        resp = requests.post(url, params=params, data=json.dumps(req_data))
        if resp.status_code != 200:
            logger.error('send TemplateMessage(%s) failed -- %s %s' % (self.key, resp.status_code, resp.content))
            return

        resp_json = resp.json()
        if 'errcode' not in resp_json or resp_json['errcode'] != 0:
            logger.error('send TemplateMessage(%s) failed -- %s' % (self.key, json.dumps(resp_json)))
            return

        logger.debug('send message pass - %s %s ' % (self.key, json.dumps(data)))
        # 设置返回
        return True
