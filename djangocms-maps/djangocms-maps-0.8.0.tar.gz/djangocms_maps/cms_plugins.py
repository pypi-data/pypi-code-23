from django.utils.translation import ugettext_lazy as _

from cms.plugin_base import CMSPluginBase
from cms.plugin_pool import plugin_pool

from .forms import MapsForm
from .models import Maps
from .settings import API_KEYS


class MapsPlugin(CMSPluginBase):
    model = Maps
    name = _("Maps")
    render_template = "djangocms_maps/maps.html"
    admin_preview = False
    form = MapsForm
    fieldsets = (
        (None, {
            'fields': (
                'title',
                ('address', 'city'),
                ('zipcode', 'zoom',),
                'content',
                ('lat', 'lng'),
            ),
        }),
        (_('Advanced'), {
            'fields': (
                ('map_provider', 'info_window'),
                ('width', 'height'),
                # ('route_planer', 'route_planer_title'),
                ('scrollwheel', 'double_click_zoom', 'draggable',
                 'keyboard_shortcuts'),
                ('pan_control', 'zoom_control', 'street_view_control',
                 'layers_control', 'scale_bar'),
                'style',
            ),
        }),
    )

    def render(self, context, instance, placeholder):
        context.update({
            'api_key': API_KEYS[instance.map_provider],
            'object': instance,
            'placeholder': placeholder,
        })
        return context


plugin_pool.register_plugin(MapsPlugin)
