from django.contrib.sites.shortcuts import get_current_site
from .models import ThemeSettings


def pcart_settings(request):
    site = get_current_site(request)
    _assets = {'css': [], 'js': []}
    try:
        theme_settings = ThemeSettings.objects.get(site=site)
        _settings = theme_settings.data.get('current', {})
        _assets = {
            'css': theme_settings.get_assets_with_extension('css'),
            'js': theme_settings.get_assets_with_extension('js'),
        }
    except ThemeSettings.DoesNotExist:
        _settings = {}
    context = {
        'site': site,
        'settings': _settings,
        'assets': _assets,
    }
    return context
