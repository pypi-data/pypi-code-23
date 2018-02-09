# -*- coding: utf-8 -*-

from plone import api


def install_recaptcha(context):
    profile_id = 'profile-plone.formwidget.recaptcha:default'
    setup = api.portal.get_tool('portal_setup')
    setup.runAllImportStepsFromProfile(profile_id)
