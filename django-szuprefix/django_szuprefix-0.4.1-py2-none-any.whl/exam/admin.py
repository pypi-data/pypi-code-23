from django.contrib import admin

from . import models


class PaperAdmin(admin.ModelAdmin):
    list_display = ('title', 'is_active', 'create_time')
    raw_id_fields = ('party', 'user')
    search_fields = ("title",)
    readonly_fields = ('party',)


admin.site.register(models.Paper, PaperAdmin)


class AnswerAdmin(admin.ModelAdmin):
    list_display = ('paper', 'user', 'create_time')
    raw_id_fields = ('party', 'user', 'paper')
    search_fields = ("paper.title",)
    # readonly_fields = ('party',)


admin.site.register(models.Answer, AnswerAdmin)


class StatAdmin(admin.ModelAdmin):
    list_display = ('paper',)
    raw_id_fields = ('party', 'paper')


admin.site.register(models.Stat, StatAdmin)


class PerformanceAdmin(admin.ModelAdmin):
    list_display = ('paper', 'user', 'create_time')
    raw_id_fields = ('party', 'user', 'paper')
    search_fields = ("paper.title",)
    # readonly_fields = ('party',)


admin.site.register(models.Performance, PerformanceAdmin)
