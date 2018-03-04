"""
Default settings for djangcms_maps
"""
import json
from django.conf import settings
from django.utils.translation import ugettext_lazy as _

BINGMAPS_API_KEY = getattr(settings, 'MAPS_BINGMAPS_API_KEY', '')
GOOGLEMAPS_API_KEY = getattr(settings, 'MAPS_GOOGLEMAPS_API_KEY', '')
HERE_API_KEY = getattr(settings, 'MAPS_HERE_API_KEY', '')
MAPBOX_API_KEY = getattr(settings, 'MAPS_MAPBOX_API_KEY', '')
VIAMICHELIN_API_KEY = getattr(settings, 'MAPS_VIAMICHELIN_API_KEY', '')

API_KEYS = {
    'bingmaps': BINGMAPS_API_KEY,
    'googlemaps': GOOGLEMAPS_API_KEY,
    'here': json.dumps(HERE_API_KEY),
    'mapbox': MAPBOX_API_KEY,
    'viamichelin': VIAMICHELIN_API_KEY,
}

PROVIDERS = getattr(settings, 'MAPS_PROVIDERS', [
    ('mapbox', _('Mapbox OSM (API key required)')),
    ('bingmaps', _('Bing Maps (API key required)')),
    ('googlemaps', _('Google Maps (API key required)')),
    ('here', _('HERE WeGo (API key required)')),
    ('viamichelin', _('ViaMichelin (API key required)')),
])
