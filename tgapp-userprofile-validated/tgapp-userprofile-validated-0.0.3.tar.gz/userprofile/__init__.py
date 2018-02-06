# -*- coding: utf-8 -*-
"""The userprofile package"""
from tg.configuration import milestones
from tgext.pluggable import plug
from tgext.pluggable import plugged

from userprofile import model


def plugme(app_config, options):
    app_config['_pluggable_userprofile_config'] = options
    milestones.config_ready.register(model.configure_models)

    if 'resetpassword' not in plugged(config=app_config):
        plug(app_config, 'resetpassword')

    return dict(appid='userprofile', global_helpers=False)
