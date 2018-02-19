from django.contrib import admin

from .models import LAU, NUTS


class NUTSRelatedFieldListFilter(admin.RelatedFieldListFilter):
    nuts_levels = [0]

    def __init__(self, field, request, params, model, model_admin, field_path):
        other_model = admin.utils.get_model_from_relation(field)
        self.lookup_kwarg = '%s__%s__startswith' % (field_path, field.target_field.name)
        self.lookup_kwarg_isnull = '%s__isnull' % field_path
        self.lookup_val = request.GET.get(self.lookup_kwarg)
        self.lookup_val_isnull = request.GET.get(self.lookup_kwarg_isnull)
        super(admin.RelatedFieldListFilter, self).__init__(
            field, request, params, model, model_admin, field_path)
        self.lookup_choices = self.field_choices(field, request, model_admin)
        if hasattr(field, 'verbose_name'):
            self.lookup_title = field.verbose_name
        else:
            self.lookup_title = other_model._meta.verbose_name
        self.title = self.lookup_title
        self.empty_value_display = model_admin.get_empty_value_display()

    def field_choices(self, field, request, model_admin):
        return field.get_choices(
            include_blank=False,
            limit_choices_to=(
                {'level__in': self.nuts_levels}
                if len(self.nuts_levels) > 1
                else {'level': self.nuts_levels[0]}
            ),
        )


class NUTSRelatedOnlyFieldListFilter(NUTSRelatedFieldListFilter):
    def field_choices(self, field, request, model_admin):
        all_codes = set(
            model_admin.get_queryset(request).distinct()
            .values_list('%s__code' % self.field_path, flat=True)
        )
        codes = set()
        for code in all_codes:
            for level in self.nuts_levels:
                if len(code) >= level + 2:
                    codes.add(code[:level + 2])
        return field.get_choices(
            include_blank=False,
            limit_choices_to=({'code__in': codes}),
        )


class LAUAdmin(admin.ModelAdmin):
    list_display = ('code', 'name', 'local_name', 'nuts1', 'nuts2', 'nuts3', 'nuts4')
    search_fields = ('nuts__code', 'code', 'name', 'local_name')


class NUTSAdmin(admin.ModelAdmin):
    list_display = ('code', 'name', 'level')
    list_filter = ('level',)
    search_fields = ('code', 'name')


admin.site.register(LAU, LAUAdmin)
admin.site.register(NUTS, NUTSAdmin)
