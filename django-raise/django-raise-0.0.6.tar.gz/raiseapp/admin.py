from django.contrib import admin

from . import models


admin.site.register([
    models.Campaign,
    models.Reward,
    models.Reminder,
    models.Pledge,
])
