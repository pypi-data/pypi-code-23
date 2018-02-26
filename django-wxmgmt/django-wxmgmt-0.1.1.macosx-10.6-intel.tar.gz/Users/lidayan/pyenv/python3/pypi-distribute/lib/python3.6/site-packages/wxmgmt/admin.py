# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin
from .models import Tenant, Account, MessageTemplate
from django.contrib import messages

# Register your models here.
@admin.register(Tenant)
class TenantAdmin(admin.ModelAdmin):
    list_display = [
        'appid', 'name', 'enable', 'access_token_expired_at',
        'jsapi_ticket_expired_at', 'updated_at', 'created_at'
    ]
    filter_horizontal = ['managers']
    list_display_links = ('appid',)
    list_editable = ('name', 'enable')
    actions = ['get_msg_tpls', 'get_menu', 'delete_menu', 'create_menu', 'get_account']

    def get_msg_tpls(self, request, queryset):
        status = 'success'
        for tenant in queryset:
            tpls = tenant.get_msg_tpls()
            if not tpls:
                self.message_user(request, u'同步公众号（%s）的消息模板失败' % tenant.name, level=messages.ERROR)
            for item in tpls:
                MessageTemplate.sync_tpl(tenant, item)
        if status == 'success':
            self.message_user(request, u'同步公众号（%s）的消息模板成功', level=messages.INFO)
    get_msg_tpls.short_description = "获取公众号的消息模板"

    def get_menu(self, request, queryset):
        status = 'success'
        for tenant in queryset:
            if not tenant.get_menu():
                status = 'failed'
                self.message_user(request, u'获取公众号（%s）的menu失败' % tenant.name, level=messages.ERROR)
        if status == 'success':
            self.message_user(request, u'获取公众号的menu成功', level=messages.INFO)
    get_menu.short_description = "获取公众号的自定义菜单"

    def delete_menu(self, request, queryset):
        status = 'success'
        for tenant in queryset:
            if not tenant.delete_menu():
                status = 'failed'
                self.message_user(request, u'删除公众号（%s）的menu失败' % tenant.name, level=messages.ERROR)
        if status == 'success':
            self.message_user(request, u'删除公众号的menu成功', level=messages.INFO)
    delete_menu.short_description = '删除公众号的自定义菜单'

    def create_menu(self, request, queryset):
        status = 'success'
        for tenant in queryset:
            if not tenant.create_menu():
                status = 'failed'
                self.message_user(request, u'创建公众号（%s）的menu失败' % tenant.name, level=messages.ERROR)
        if status == 'success':
            self.message_user(request, u'创建公众号的menu成功', level=messages.INFO)
    create_menu.short_description = '创建公众号的自定义菜单'

    def get_account(self, request, queryset):
        status = 'success'
        for tenant in queryset:
            for openid in tenant.get_openids():
                if not Account.sync_account(tenant, openid):
                    status = 'failed'
                    self.message_user(request, u'同步公众号（%s）的关注账号失败' % tenant.name, level=messages.ERROR)
        if status == 'success':
            self.message_user(request, u'同步公众号的关注账号成功', level=messages.INFO)
    get_account.short_description = '获取公众号的关注用户'



@admin.register(Account)
class AccountAdmin(admin.ModelAdmin):
    list_display = ['nickname', 'tenant', 'openid', 'sex',
        'city', 'province', 'status', 'subscribed_at', 'created_at']
    list_filter = ('tenant', 'status')


@admin.register(MessageTemplate)
class MessageTemplateAdmin(admin.ModelAdmin):
    list_display = ['template_id', 'tenant', 'title', 'key', 'primary_industry', 'deputy_industry']

