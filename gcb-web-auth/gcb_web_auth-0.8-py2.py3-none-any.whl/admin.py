from django.contrib import admin
from gcb_web_auth.models import OAuthService, OAuthToken, DukeDSAPIToken, GroupManagerConnection

# Register your models here.
admin.site.register(OAuthService)
admin.site.register(OAuthToken)
admin.site.register(DukeDSAPIToken)
admin.site.register(GroupManagerConnection)
