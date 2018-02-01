# -*- coding: utf-8 -*-
"""The userprofile package"""
from tg.configuration import milestones
from userprofile import model


def plugme(app_config, options):
    app_config['_pluggable_userprofile_config'] = options
    milestones.config_ready.register(model.configure_models)
    return dict(appid='userprofile', global_helpers=False)
