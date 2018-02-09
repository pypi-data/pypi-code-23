# -*- coding: utf-8
from django.conf import settings as default_settings
from appconf import AppConf


class GenomixUsersConf(AppConf):
    CREATE_PROFILE_ON_SAVE = True

    class Meta:
        proxy = True

    def configure_create_profile_on_save(self, value):
        return getattr(default_settings, 'CREATE_PROFILE_ON_SAVE', value)


settings = GenomixUsersConf()
