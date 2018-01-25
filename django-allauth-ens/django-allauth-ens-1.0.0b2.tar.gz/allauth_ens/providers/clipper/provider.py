# -*- coding: utf-8 -*-
from allauth.account.models import EmailAddress
from allauth.socialaccount.providers.base import ProviderAccount

from allauth_cas.providers import CASProvider


class ClipperAccount(ProviderAccount):
    pass


class ClipperProvider(CASProvider):
    id = 'clipper'
    name = 'Clipper'
    account_class = ClipperAccount

    def extract_email(self, data):
        uid, extra = data
        return '{}@clipper.ens.fr'.format(uid.strip().lower())

    def extract_common_fields(self, data):
        common = super(ClipperProvider, self).extract_common_fields(data)
        common['email'] = self.extract_email(data)
        return common

    def extract_email_addresses(self, data):
        return [
            EmailAddress(
                email=self.extract_email(data),
                verified=True, primary=True,
            ),
        ]

    def extract_extra_data(self, data):
        extra_data = super(ClipperProvider, self).extract_extra_data(data)
        extra_data['email'] = self.extract_email(data)
        return extra_data

    def message_suggest_caslogout_on_logout(self, request):
        return (
            self.get_settings()
            .get('MESSAGE_SUGGEST_CASLOGOUT_ON_LOGOUT', True)
        )


provider_classes = [ClipperProvider]
